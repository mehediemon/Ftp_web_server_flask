pipeline {
    agent any
    stages {
        stage('Build') {
            when {
                branch 'main'
            }
            steps {
                echo "====== BUILD STAGE ======"
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    venv/bin/pip install --no-deps -r requirements.txt
                '''
            }
        }
        stage('Transfer Files to Remote Server') {
            steps {
                script {
                    echo 'Transferring files to remote server...'
                    sh """
                        scp -i devtestkey.pem -r . ubuntu@13.126.82.73:/mnt/
                    """
                }
            }
        }

        stage('Deploy on Remote Server') {
            steps {
                script {
                    echo 'Deploying application on remote server...'
                    sh """
                        ssh -i devtestkey.pem ubuntu@13.126.82.73 'cd /mnt/ && docker-compose up -d'
                    """
                }
            }
        }
    }
}