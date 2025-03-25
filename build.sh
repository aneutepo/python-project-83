#!/usr/bin/env bash
# Устанавливаем uv и зависимости
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
make install
