pipeline {
    agent any
    stages {
        stage('Clone Code') {
            steps {
                git branch: 'main', url: 'https://github.com/ravindrathakur19/vulnscan-pro.git'
            }
        }
        stage('Docker Build') {
            steps {
                sh 'docker build -t ravi12t/vuln-scanner:latest .'
            }
        }
        stage('Docker Push') {
            steps {
                sh 'docker push ravi12t/vuln-scanner:latest'
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker stop vuln-scanner || true'
                sh 'docker rm vuln-scanner || true'
                sh 'docker run -d -p 5000:5000 --name vuln-scanner ravi12t/vuln-scanner:latest'
            }
        }
    }
}