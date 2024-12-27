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
    }
}