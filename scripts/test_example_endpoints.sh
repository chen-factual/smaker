#! /bin/bash

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EXAMPLE_DIR=$DIR/../examples

cd $EXAMPLE_DIR

OUTPUT_PATH=output/test-output-path
SOURCE=test-source-xyz
set -x

smaker fly \
    -c simple/config.json \
    -s simple/Snakefile \
    --source=$SOURCE \
    --output-path=$OUTPUT_PATH \
    -F \
    -v

smaker fly \
    -c simple/config.json \
    -s simple/Snakefile \
    --source $SOURCE \
    --output-path $OUTPUT_PATH \
    -F \
    -v

smaker fly \
    -c simple/config.json \
    -s Snakefile \
    --module hello_world/Snakefile.hello \
    -F \
    --quiet

for endpoint in $(smaker list); do
    smaker run -e $endpoint --quiet -F
done
set +x


echo "Successful dryruns for example endpoints"
