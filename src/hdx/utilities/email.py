"""Utility class to simplify sending emails"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import expanduser, join
from typing import Any, List, Optional, Union

try:
    from email_validator import validate_email
except ImportError:
    validate_email = None

from hdx.utilities.loader import load_json, load_yaml

logger = logging.getLogger(__name__)


class EmailConfigurationError(Exception):
    pass


class Email:
    """
    Emailer utility. Parameters in dictionary or file (eg. yaml below):
     | connection_type: "ssl"   ("ssl" for smtp ssl or "lmtp", otherwise basic smtp is assumed)
     | host: "localhost"
     | port: 123
     | local_hostname: "mycomputer.fqdn.com"
     | timeout: 3
     | username: "user"
     | password: "pass"
     | sender: "a@b.com"    (if not supplied username is used as sender)

    Args:
        **kwargs: See below
        email_config_dict (dict): HDX configuration dictionary OR
        email_config_json (str): Path to JSON HDX configuration OR
        email_config_yaml (str): Path to YAML HDX configuration. Defaults to ~/hdx_email_configuration.yml.
    """

    default_email_config_yaml = join(
        expanduser("~"), "hdx_email_configuration.yml"
    )

    def __init__(self, **kwargs: Any) -> None:
        email_config_found = False
        email_config_dict = kwargs.get("email_config_dict", None)
        if email_config_dict:
            email_config_found = True
            logger.info("Loading email configuration from dictionary")

        email_config_json = kwargs.get("email_config_json", "")
        if email_config_json:
            if email_config_found:
                raise EmailConfigurationError(
                    "More than one email configuration file given!"
                )
            email_config_found = True
            logger.info(
                f"Loading email configuration from: {email_config_json}"
            )
            email_config_dict = load_json(email_config_json)

        email_config_yaml = kwargs.get("email_config_yaml", None)
        if email_config_found:
            if email_config_yaml:
                raise EmailConfigurationError(
                    "More than one email configuration file given!"
                )
        else:
            if not email_config_yaml:
                logger.info(
                    "No email configuration parameter. Using default email configuration path."
                )
                email_config_yaml = Email.default_email_config_yaml
            logger.info(
                f"Loading email configuration from: {email_config_yaml}"
            )
            email_config_dict = load_yaml(email_config_yaml)

        self.connection_type = email_config_dict.get("connection_type", "smtp")
        self.host = email_config_dict.get("host", "")
        self.port = email_config_dict.get("port", 0)
        self.local_hostname = email_config_dict.get("local_hostname")
        self.timeout = email_config_dict.get("timeout")
        self.source_address = email_config_dict.get("source_address")
        self.username = email_config_dict.get("username")
        self.password = email_config_dict.get("password")
        self.sender = email_config_dict.get("sender", self.username)
        self.server = None

    def __enter__(self) -> "Email":
        """
        Return Email object for with statement

        Returns:
            None

        """
        return self

    def __exit__(self, *args: Any) -> None:
        """
        Close Email object for end of with statement

        Args:
            *args: Not used

        Returns:
            None

        """

    def connect(self) -> None:
        """
        Connect to server

        Returns:
            None

        """
        if self.connection_type.lower() == "ssl":
            self.server = smtplib.SMTP_SSL(
                host=self.host,
                port=self.port,
                local_hostname=self.local_hostname,
                timeout=self.timeout,
                source_address=self.source_address,
            )
        elif self.connection_type.lower() == "lmtp":
            self.server = smtplib.LMTP(
                host=self.host,
                port=self.port,
                local_hostname=self.local_hostname,
                source_address=self.source_address,
            )
        else:
            self.server = smtplib.SMTP(
                host=self.host,
                port=self.port,
                local_hostname=self.local_hostname,
                timeout=self.timeout,
                source_address=self.source_address,
            )
        self.server.login(self.username, self.password)

    def close(self) -> None:
        """
        Close connection to email server

        Returns:
            None

        """
        self.server.quit()

    @staticmethod
    def get_normalised_emails(recipients: Union[str, List[str]]) -> List[str]:
        """
        Get list of normalised emails

        Args:
            recipients (Union[str, List[str]]): Email recipient(s)

        Returns:
            List[str]: Normalised emails

        """
        if isinstance(recipients, str):
            recipients = [recipients]
        if validate_email is None:
            return recipients
        normalised_recipients = list()
        for recipient in recipients:
            v = validate_email(
                recipient, check_deliverability=True
            )  # validate and get info
            normalised_recipients.append(
                v["email"]
            )  # replace with normalized form
        return normalised_recipients

    def send(
        self,
        to: Union[str, List[str]],
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        sender: Optional[str] = None,
        cc: Union[str, List[str], None] = None,
        bcc: Union[str, List[str], None] = None,
        **kwargs: Any,
    ) -> None:
        """
        Send email. to, cc and bcc take either a string email address or a list of
        string email addresses. cc and bcc default to None.

        Args:
            to (Union[str, List[str]]): Email recipient(s)
            subject (str): Email subject
            text_body (str): Plain text email body
            html_body (Optional[str]): HTML email body
            sender (Optional[str]): Email sender. Defaults to global sender.
            cc (Union[str, List[str], None]): Email cc. Defaults to None.
            bcc (Union[str, List[str], None]): Email bcc. Defaults to None.
            **kwargs: See below
            mail_options (List): Mail options (see smtplib documentation)
            rcpt_options (List): Recipient options (see smtplib documentation)

        Returns:
            None

        """
        if sender is None:
            sender = self.sender
        v = validate_email(
            sender, check_deliverability=False
        )  # validate and get info
        sender = v["email"]  # replace with normalized form

        if html_body is not None:
            msg = MIMEMultipart("alternative")
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            msg.attach(part1)
            msg.attach(part2)
        else:
            msg = MIMEText(text_body)
        msg["Subject"] = subject
        msg["From"] = sender

        normalised_to = self.get_normalised_emails(to)
        msg["To"] = ", ".join(normalised_to)

        if cc is not None:
            normalised_cc = self.get_normalised_emails(cc)
            msg["Cc"] = ", ".join(normalised_cc)
            normalised_to.extend(normalised_cc)

        if bcc is not None:
            normalised_bcc = self.get_normalised_emails(bcc)
            normalised_to.extend(normalised_bcc)

        # Perform operations via server
        self.connect()
        self.server.sendmail(sender, normalised_to, msg.as_string(), **kwargs)
        self.close()
