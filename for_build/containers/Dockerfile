FROM simexp/niak-cog:1.0.1

LABEL maintainer="Obaï Bin Ka'b Ali @aliobaibk" \
    version=1.3.0



# Environment
ENV SPARK_DIR=/usr/local/Multi_FunkIm/spark



# Download and install SPARK
RUN mkdir -p "$SPARK_DIR" && \
    echo 'Download SPARK library...' && \
    wget -q "https://api.github.com/repos/multifunkim/spark-matlab/releases/latest" -O /tmp/spark.latest && \
    zip_url="$(grep zipball_url /tmp/spark.latest | cut -d '"' -f 4)" && \
    wget -q "$zip_url" -O /tmp/spark-lib.zip && \
    unzip -q /tmp/spark-lib.zip -d /tmp && \
    mv /tmp/multifunkim-spark-matlab*/* "$SPARK_DIR" && \
    rm -rf /tmp/spark-lib.zip /tmp/multifunkim-spark-matlab* && \
    \
    echo 'Download SPARK main function...' && \
    wget -q -P "$SPARK_DIR" "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/main/spark.m" && \
    \
    echo 'Download SPARK utilities...' && \
    wget -q -P "$SPARK_DIR"/util "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/util/prependFileToFile.m" && \
    wget -q -P "$SPARK_DIR"/util "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/util/str2RegSpacedVector.m" && \
    mkdir "$SPARK_DIR"/util/psom_gb && \
    wget -q -P "$SPARK_DIR"/util/psom_gb "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/util/psom_gb/spark_psom_gb.m" && \
    \
    echo 'Configure SPARK...' && \
    echo addpath\(genpath\(\'$SPARK_DIR\'\)\)\; >> /etc/octave.conf && \
    chmod -R 755 $SPARK_DIR