FROM parity/parity:stable

ADD ./config.toml /root/.local/share/io.parity.ethereum/

EXPOSE 8545 8546 8180 30303

# OG parity Dockerfile already runs parity, so just pass args
CMD ["--config", "/root/.local/share/io.parity.ethereum/config.toml"]