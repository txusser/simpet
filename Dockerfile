FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/home
ENV SIMPET_DIR=$HOME/simpet

COPY . $SIMPET_DIR

RUN apt-get update && \
    apt-get -y -q install \
    sudo \
    git[all] \
    vim \
    wget \
	make \
	python3-pip && \
	git clone https://github.com/YerePhy/dotfiles.git $HOME/dotfiles && \
	cp $HOME/dotfiles/.vimrc $HOME/.vimrc && rm -rf $HOME/dotfiles && \
	pip install -r $SIMPET_DIR/requirements.txt && \
	cd $SIMPET_DIR && make deps && make install && \
	mv $SIMPET_DIR/include $HOME && rm -rf $SIMPET_DIR

ENTRYPOINT bash
