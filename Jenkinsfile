pipeline {
    agent any

    options {
        // Cegah dua build berjalan bersamaan dan berebut nama container yang sama
        disableConcurrentBuilds()
    }

    environment {
        PYTHONUNBUFFERED = '1'
        REGISTRY_NAME    = 'python-crud-api'
        CONTAINER_NAME   = 'production-api-container'
        PORT_MAPPING     = '5000:5000'
        VOLUME_NAME      = 'production-api-data'
        DOCKER_NETWORK   = 'jenkins-net'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
                script {
                    // Tugas D: tag image berbasis commit SHA
                    env.GIT_SHORT_SHA = sh(script: 'git rev-parse --short=7 HEAD',
                                           returnStdout: true).trim()
                }
                echo "Commit: ${env.GIT_SHORT_SHA}"
            }
        }

        stage('2. Code Syntax Verification') {
            steps {
                sh 'python3 -m py_compile app.py test_app.py'
            }
        }

        stage('3. Unit Test') {
            // Tugas D: test otomatis health check, validasi POST, GET /messages/{id}
            steps {
                sh 'python3 -m unittest -v test_app.py'
            }
        }

        stage('4. Build Docker Image') {
            steps {
                sh 'docker build -t ${REGISTRY_NAME}:${BUILD_NUMBER} .'
                sh 'docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:sha-${GIT_SHORT_SHA}'
                sh 'docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:latest'
            }
        }

        stage('5. Automated Deployment') {
            steps {
                sh '''
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker volume create ${VOLUME_NAME}
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --network ${DOCKER_NETWORK} \
                        -p ${PORT_MAPPING} \
                        -v ${VOLUME_NAME}:/var/lib/backend_data \
                        --restart unless-stopped \
                        ${REGISTRY_NAME}:latest
                '''
            }
        }

        stage('6. Health Check') {
            steps {
                // Jenkins berjalan di container, jadi "localhost" = container Jenkins.
                // API dijangkau lewat nama container di network jenkins-net.
                sh '''
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                        if curl -fsS http://${CONTAINER_NAME}:5000/health; then
                            echo; echo "Health check OK (percobaan $i)"; break
                        fi
                        [ $i -eq 10 ] && { echo "Health check gagal"; exit 1; }
                        sleep 2
                    done
                '''
                // Bandingkan dengan Docker HEALTHCHECK bawaan image
                sh '''
                    for i in $(seq 1 15); do
                        STATUS=$(docker inspect -f '{{.State.Health.Status}}' ${CONTAINER_NAME})
                        echo "Docker HEALTHCHECK status: $STATUS"
                        [ "$STATUS" = "healthy" ] && break
                        [ "$STATUS" = "unhealthy" ] && exit 1
                        sleep 2
                    done
                '''
                sh 'docker logs --tail 20 ${CONTAINER_NAME}'
                sh 'docker images ${REGISTRY_NAME}'
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. Image: ${REGISTRY_NAME}:${BUILD_NUMBER} / sha-${env.GIT_SHORT_SHA}"
        }
        failure {
            echo 'Pipeline failed. Inspect Console Output.'
            sh 'docker logs --tail 50 ${CONTAINER_NAME} || true'
        }
    }
}
