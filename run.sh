#!/bin/bash
set -e

cd "$(dirname "$0")"

uname_out="$(uname -s)"
case "${uname_out}" in
    Linux*)     C_OS_TYPE=Linux;;
    Darwin*)    C_OS_TYPE=Mac;;
    *)          C_OS_TYPE="UNKNOWN:${uname_out}"
esac

PROJECT_NAME=${PWD##*/}
PROJECT_VERSION='1'
PROJECT_STACK=

main() {
    local CMD=$1
    shift
    echo -e "Run $PROJECT_NAME $PROJECT_VERSION on $C_OS_TYPE\n"

    if [[ ! -f .env ]] ; then
        echo "Please provide .env to run the stack"
        exit 1
    fi

    export $(cat .env | grep -v ^# | xargs)

    case $CMD in
        setup) setup $@;;
        build) build $@;;
        stack) stack $@;;
        test) test $@;;
        generate) generate $@;;
        clean) clean $@;;
        coverage) coverage $@;;
        docker) docker_ $@;;
        *) echo "Run as: $0 command
Possible commands:
    setup    check/install host prerequisties
    stack    run the specified stack
    test     run tests
    generate generate configuration files for the current environment
    clean    clean the stack
    docker   docker operations
    "; exit;;
    esac
}

setup() {
    local DOCKER_VERSION=${1:-17.12}
    apt-get update -qq
    apt-get install -y curl apt-transport-https

    mkdir -p /etc/docker

    echo '{
        "log-driver": "json-file",
        "log-opts": {
            "max-size": "10m",
            "max-file": "2"
        }
    }' > /etc/docker/daemon.json

    echo "Installing Docker..."

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
    apt install -y software-properties-common
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable"
    apt-get update -qq
    apt-get install -y docker-ce=$(apt-cache madison docker-ce | grep $DOCKER_VERSION | head -1 | awk '{print $3}')
    apt-get install python-pip -y
    pip install docker-compose

    systemctl restart docker

    echo "Done"
}

check_stack() {
    local STACK=$1
    shift

    if [[ ! "$STACK" =~ ^(dev|stage|prod|test)$ ]]; then
        echo "$0 stack [dev|stage|prod|test]";
        exit 1
    fi
}

stack() {
    local STACK=dev

    if [[ "$#" > 1 ]]; then
        local STACK=$1
        shift
    fi

    check_stack $STACK

    PROJECT_STACK=$STACK

    generate_compose $STACK
    docker_build

    mkdir -p "tmp/coverage";

    docker-compose up -d

    initialize_db_mysql

    echo "Done"
}

initialize_db_mysql() {
    echo "start init db..."
    echo "start..."
    until docker-compose run --rm test sh -c "mysql -h $MYSQL_HOST -u $MYSQL_USER -p\"$MYSQL_PASSWORD\" -e '\q'"; do
        echo "Waiting for MySQL..."
        sleep 1
    done
    echo "inited db..."
}

clean() {
    docker-compose down -v
    docker-compose rm -fv

    docker images --format '{{.Repository}}' | grep $PROJECT_NAME | xargs docker rmi
}

generate() {
    local CMD=$1
    shift

    case $CMD in
        compose) generate_compose $@;;
        *) echo "$0 generate [compose]"; exit;;
    esac
}

generate_compose() {
    local STACK=dev

    if [[ "$#" > 1 ]]; then
        local STACK=$1
        shift
    fi

    check_stack $STACK

    PROJECT_STACK=$STACK

    local DOCKER_COMPOSE_YAML=build/docker-compose.$STACK.yaml
    if [[ ! -f $DOCKER_COMPOSE_YAML ]] ; then
        DOCKER_COMPOSE_YAML=build/docker-compose.yaml
    fi

    rm -f docker-compose.yaml
    cp $DOCKER_COMPOSE_YAML docker-compose.yaml

    for env_variable in PROJECT_NAME \
                        PROJECT_VERSION \
                        PROJECT_STACK; do
        if [[ ${!env_variable} ]]; then
            if [[ "$C_OS_TYPE" == 'Linux' ]]; then
                sed -i "s~__${env_variable}__~${!env_variable}~g" docker-compose.yaml
            else
                sed -i '' "s~__${env_variable}__~${!env_variable}~g" docker-compose.yaml
            fi
        fi
    done
}

coverage() {
    local CMD=$1
    shift

    case $CMD in
        report) coverage_report $@;;
        clean) coverage_clean $@;;
        *) echo "$0 coverage [report|clean]"; exit;;
    esac
}

coverage_report() {
    local COVERAGE_RCFILE=share/coverage/.coveragerc
    local COVERAGE_DATA=tmp/coverage/

    docker-compose run \
        --rm test sh -c "coverage combine --rcfile=$COVERAGE_RCFILE $COVERAGE_DATA && coverage report --rcfile=$COVERAGE_RCFILE && coverage html --rcfile=$COVERAGE_RCFILE"
}

coverage_clean() {
    rm -rf "tmp/coverage";
    mkdir -p "tmp/coverage";
}

test() {
    local CMD=$1
    shift

    case $CMD in
        style) test_style $@;;
        functional) test_functional $@;;
        unit) test_unit $@;;
        ci) test_ci $@;;
        *) echo "$0 test [style|functional|unit|ci]"; exit;;
    esac
}

test_style() {
    docker run \
        -v ${PWD}:/code \
        --rm virtualenv-test:latest \
        flake8 --config=test/style/.flake8 .
}

test_functional() {
    mkdir -p "tmp/coverage";

    docker-compose run \
        -v ${PWD}:/code \
        --rm test \
        pytest -p no:cacheprovider test/functional "$@"
}

test_unit() {
    mkdir -p "tmp/coverage";

    docker-compose run \
        -v ${PWD}:/code \
        --rm test \
        pytest -p no:cacheprovider test/unit "$@"
}

test_ci() {
    test_style

    coverage_clean

    local TEST_STATUS=0

    test_unit --junitxml=./tmp/test/unit/report.xml || TEST_STATUS=$?
    test_functional --junitxml=./tmp/test/functional/report.xml || TEST_STATUS=$?

    coverage_report
    exit $TEST_STATUS
}

docker_() {
    local CMD=$1
    shift

    case $CMD in
        build) docker_build $@;;
        push) docker_push $@;;
        *) echo "$0 docker [build|push]"; exit;;
    esac
}

docker_build() {
    docker build -t virtualenv:latest -f build/virtualenv/Dockerfile build/virtualenv
    docker build -t virtualenv-test:latest -f build/virtualenv/Dockerfile-test build/virtualenv
}

docker_push() {
    docker build -f build/deploy/Dockerfile -t $PROJECT_NAME:$PROJECT_VERSION --build-arg IMAGE_TAG_VIRTUALENV=virtualenv:latest .
}

main "$@"
