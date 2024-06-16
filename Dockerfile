# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.10-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# 0. Install essential packages
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        unixodbc-dev \
        jq \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

# 1. Install Chrome (root image is debian)
# See https://stackoverflow.com/questions/49132615/installing-chrome-in-docker-file
# Install Chrome (root image is debian)
ARG CHROME_VERSION="google-chrome-stable"
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install \
    ${CHROME_VERSION:-google-chrome-stable} \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Install Chrome driver used by Selenium
RUN LATEST=$(wget -q -O - https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json \
 | jq -r '.channels.Stable.downloads.chrome[] | select(.platform=="linux64").url') \ 
  && wget $LATEST \
  && unzip chrome-linux64.zip -d /usr/local/bin/ && ln -s /usr/local/bin/chromedriver /usr/local/bin/chromedriver

ENV DISPLAY=:99

COPY function_app.py ./
COPY host.json ./
COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot

# CMD ["Xvfb", ":99", "-ac", "-screen", "0", "1280x1024x16", "&", "python", "./function_app.py"]
CMD [ "python",  "./function_app.py"]

