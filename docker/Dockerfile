FROM continuumio/miniconda3:latest

MAINTAINER conda-forge <conda-forge@googlegroups.com>

# Update conda
RUN conda config --set always_yes True && \
    conda config --add channels conda-forge && \
    conda update --all && \
    conda clean --all

# install libcflib
RUN git clone https://github.com/regro/libcflib.git --depth 1 && \
    cd libcflib && \
    conda install --file requirements/run.txt && \
    python setup.py install && \
    cd .. && \
    rm -rf libcflib && \
    conda clean --all

ENTRYPOINT ["/opt/conda/bin/python", "-m", "libcflib.rest", "--port", "80"]
