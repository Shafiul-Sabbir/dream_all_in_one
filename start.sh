#!/bin/bash

# Project base path
PROJECT_DIR=~/Desktop/Dream_projects/all_in_one/all_in_one
VENV=$PROJECT_DIR/env/bin/activate

# Activate virtual environment
source $VENV

# Run Django server in a new terminal
echo "🚀 Starting Django server in a separate terminal..."
gnome-terminal -- bash -c "source $VENV && python3 $PROJECT_DIR/manage.py runserver 0.0.0.0:8010; exec bash"

# Run Celery worker
echo "⚡ Starting Celery worker..."
celery -A start_project worker --loglevel=info &
CELERY_PID=$!

# Run ngrok
echo "🌐 Starting ngrok tunnel..."
ngrok http 8010 &
NGROK_PID=$!

# Run Stripe listener
echo "💳 Starting Stripe webhook listener..."
stripe listen --forward-to localhost:8010/stripe_payments/api/v1/payments/stripe-webhook/ &
STRIPE_PID=$!

echo "✅ All services are running!"
echo "Celery PID: $CELERY_PID"
echo "Ngrok PID: $NGROK_PID"
echo "Stripe PID: $STRIPE_PID"
echo "👉 Django logs are in a separate terminal window!"

# Trap CTRL+C and stop all processes
trap "echo 'Stopping all services...'; kill $CELERY_PID $NGROK_PID $STRIPE_PID" SIGINT

# Wait for all background jobs
wait


# start command for the script
# go to the project directory where manage.py is located

# then if you are first time running the script, run:
# chmod +x start.sh

# then login to the stripe CLI with:
# stripe login

# then run the script with:
# ./start.sh

# Note: Ensure that the ngrok binary is installed and available in your PATH.
# You can download it from https://ngrok.com/download
# Make sure to have the Stripe CLI installed and configured as well.
# You can install it from https://stripe.com/docs/stripe-cli#install