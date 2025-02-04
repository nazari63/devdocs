#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Installing Rust..."
rustup default stable

echo "Installing mdbook..."
curl -L https://github.com/rust-lang/mdBook/releases/download/v0.4.44/mdbook-v0.4.44-x86_64-unknown-linux-gnu.tar.gz | tar xvz
mv mdbook "$HOME/.cargo/bin"

echo "Installing mdbook-mermaid.."
cargo install mdbook-mermaid

echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "Updating submodules..."
COMMIT=false bash "$SCRIPT_DIR/update-submodules.sh"

echo "Building..."
export PATH="$HOME/.cargo/bin:$PATH"
uv run run.py