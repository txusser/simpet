FROM ubuntu:22.04

ARG NPROC=4

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/home
ENV SIMPET_DIR=$HOME/simpet
ENV STIR_DIR=$SIMPET_DIR/submodules/STIR/STIR

COPY . $SIMPET_DIR

RUN apt-get update && \
    apt-get -y -q install \
    sudo \
    git[all] \
    git-lfs \
    vim \
    wget \
	make \
	python3-pip && \
	git clone https://github.com/YerePhy/dotfiles.git $HOME/dotfiles && \
	cp $HOME/dotfiles/.vimrc $HOME/.vimrc && rm -rf $HOME/dotfiles && \
    git config --global --add safe.directory $SIMPET_DIR && \
    git config --global --add safe.directory $STIR_DIR && \
    pip install -r $SIMPET_DIR/requirements.txt && \
    cd $SIMPET_DIR && \
    git config --local --unset user.name && \
    git config --local --unset user.email && \
    && make install NRPROC=$NPROC

ENTRYPOINT bash
