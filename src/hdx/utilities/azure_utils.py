"""All the logic around Azure blob uploads and downloads of files"""

import base64
import hashlib
import hmac
import io
import logging
from datetime import datetime
from os.path import exists
from typing import Any

try:
    import pandas as pd
    from azure.storage.blob import BlobServiceClient, ContentSettings
except ImportError:
    BlobServiceClient = None
    ContentSettings = None
    pd = None

from .downloader import Download

logger = logging.getLogger(__name__)


class AzureBlobDownload(Download):
    """Wrapper for Azure Blob download logic"""

    def download_file(
        self,
        url: str,
        account: str,
        container: str,
        key: str,
        blob: None,
        **kwargs: Any,
    ) -> str:
        """Download a blob file from an Azure Storage

        Args:
            url (str): URL for the exact blob location
            account (str): Storage account to access the blob
            container (str): Container to download from
            key (str): Key to access the blob
            blob (str): Name of the blob to be downloaded. If empty, then it is assumed to download
            the whole container.
            **kwargs: See below
            path (str): Full path to use for downloaded file instead of folder and filename.
            keep (bool): Whether to keep already downloaded file. Defaults to False.
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Dict): Parameters to pass. Defaults to None.
            timeout (float): Timeout for connecting to URL. Defaults to None (no timeout).
            headers (Dict): Headers to pass. Defaults to None.
            encoding (str): Encoding to use for text response. Defaults to None (best guess).
        """
        path = kwargs.get("path")
        keep = kwargs.get("keep", False)

        request_time = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        api_version = "2018-03-28"
        parameters = {
            "verb": "GET",
            "Content-Encoding": "",
            "Content-Language": "",
            "Content-Length": "",
            "Content-MD5": "",
            "Content-Type": "",
            "Date": "",
            "If-Modified-Since": "",
            "If-Match": "",
            "If-None-Match": "",
            "If-Unmodified-Since": "",
            "Range": "",
            "CanonicalizedHeaders": "x-ms-date:"
            + request_time
            + "\nx-ms-version:"
            + api_version
            + "\n",
            "CanonicalizedResource": "/"
            + account
            + "/"
            + container
            + "/"
            + blob,
        }

        signature = (
            parameters["verb"]
            + "\n"
            + parameters["Content-Encoding"]
            + "\n"
            + parameters["Content-Language"]
            + "\n"
            + parameters["Content-Length"]
            + "\n"
            + parameters["Content-MD5"]
            + "\n"
            + parameters["Content-Type"]
            + "\n"
            + parameters["Date"]
            + "\n"
            + parameters["If-Modified-Since"]
            + "\n"
            + parameters["If-Match"]
            + "\n"
            + parameters["If-None-Match"]
            + "\n"
            + parameters["If-Unmodified-Since"]
            + "\n"
            + parameters["Range"]
            + "\n"
            + parameters["CanonicalizedHeaders"]
            + parameters["CanonicalizedResource"]
        )
        signed_string = base64.b64encode(
            hmac.new(
                base64.b64decode(key),
                msg=signature.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()

        headers = {
            "x-ms-date": request_time,
            "x-ms-version": api_version,
            "Authorization": ("SharedKey " + account + ":" + signed_string,)
        }

        url = (
                "https://"
                + account
                + ".blob.core.windows.net/"
                + container
                + "/"
                + blob
        )

        if keep and exists(url):
            print(f"The blob URL exists: {url}")
            return path
        self.setup(
            url=url,
            stream=True,
            post=kwargs.get("post", False),
            parameters=kwargs.get("parameters"),
            timeout=kwargs.get("timeout"),
            headers=headers,
            encoding=kwargs.get("encoding"),
        )
        return self.stream_path(
            path, "Download of %s failed in retrieval of stream!" % url
        )


class AzureBlobUpload:
    """Wrapper for Azure Blob upload logic"""

    def upload_file(
        self,
        dataset_name: str,
        filename: str,
        account: str,
        container: str,
        key: str,
        data: None
    ) -> str:
        """Upload a file to a blob storage within a container for an azure storage account
        Args:
            dataset_name (str): name of the dataset within the dictionary list to upload
            filename (str): new name for the file once it is uploaded to the container
            account (str): Storage account
            container (str): Name of the container where the file will be uploaded to.
            key (str): Access key to container
            data : json type of dicts with multiple datasets or just one
        """

        blob_service = BlobServiceClient.from_connection_string(
            f"DefaultEndpointsProtocol=https;AccountName={account};AccountKey= "
            f"{key};EndpointSuffix=core.windows.net"
        )

        blob_client = blob_service.get_blob_client(
            container=container,
            blob=filename)

        try:
            stream = io.StringIO()
            df = pd.DataFrame(data[dataset_name])
            df.to_csv(stream, sep=";")
            file_to_blob = stream.getvalue()
            blob_client.upload_blob(
                file_to_blob,
                overwrite=True,
                content_settings=ContentSettings(content_type="text/csv")
            )
            logger.info("Successfully uploaded: %s" % dataset_name)
        except Exception:
            logger.error("Failed to upload dataset: %s" % dataset_name)
