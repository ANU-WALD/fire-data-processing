FROM continuumio/anaconda3:2020.02

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update && \
    apt-get install -y g++ libgdal-dev libgdal20 gdal-bin && \
    /opt/conda/bin/conda install jupyter -y --quiet && \
    conda install --yes netcdf4 xarray && \
    cd /tmp && pip install -r requirements.txt && \
    apt-get install cdo && \
    mkdir /opt/notebooks 
    # conda install --yes -c conda-forge gdal && \

# USER ubuntu

WORKDIR /opt/notebooks

CMD [ "/opt/conda/bin/jupyter","notebook","--notebook-dir=/opt/notebooks", "--ip='*'", "--port=8888","--no-browser", "--allow-root" ]

