pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Check Environment') {
            steps {
                sh 'git --version'
                sh 'docker --version'
                sh 'kubectl get nodes'
                sh 'curl http://192.168.30.10:5000/v2/_catalog'
            }
        }

        stage('Deploy') {
            steps {
                sh 'chmod +x deploy.sh'
                sh './deploy.sh build-${BUILD_NUMBER}'
            }
        }

        stage('Verify') {
            steps {
                sh 'kubectl get pods -o wide'
                sh 'kubectl get deploy chat-backend -o jsonpath="{.spec.template.spec.containers[0].image}{\\"\\n\\"}"'
                sh 'kubectl get deploy chat-frontend -o jsonpath="{.spec.template.spec.containers[0].image}{\\"\\n\\"}"'
            }
        }
    }

    post {
        success {
            echo 'Deploy success. Visit: http://192.168.30.10:30080'
        }

        failure {
            echo 'Deploy failed. Check Jenkins console output.'
        }
    }
}