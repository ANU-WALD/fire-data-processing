FROM joelrahman/conda-python-science

RUN mkdir /opt/fire && cd /opt/fire
    # conda install --yes -c conda-forge gdal && \

COPY . /opt/fire

# USER ubuntu

WORKDIR /opt/fire

CMD [ "python","update_fmc.py"]

