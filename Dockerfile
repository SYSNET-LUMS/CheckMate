FROM ubuntu:22.04

# Set the working directory for CheckMate
WORKDIR /home/ubuntu

# Update and upgrade packages
RUN apt-get update && apt-get upgrade -y

# Install dependencies
RUN apt-get install -y \
    git \
    autoconf \
    perl \
    graphviz \
    clang \
    python3.10 \
    python3-pip

# Copy project files to CheckMate folder
COPY . CheckMate

# Set permissions and execute the fused script
WORKDIR /home/ubuntu
RUN chmod u+x /home/ubuntu/CheckMate/install_fused_script.sh && \
    /home/ubuntu/CheckMate/install_fused_script.sh && \
    cp /home/ubuntu/fused-checkmate/build/fused /home/ubuntu/CheckMate/fusedBin/

# Install Egypt in a separate folder
WORKDIR /home/ubuntu/egypt
RUN wget https://www.gson.org/egypt/download/egypt-1.11.tar.gz && \
    tar -xvf egypt-1.11.tar.gz && \
    cd egypt-1.11 && \
    perl Makefile.PL && \
    make && \
    make install

# Return to CheckMate directory and install Python dependencies
WORKDIR /home/ubuntu/CheckMate
RUN pip install -r requirements.txt

# Default command to start a terminal for the user
CMD ["/bin/bash"]
