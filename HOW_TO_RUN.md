# HOW TO RUN

This guide provides step-by-step instructions to set up and run the TutupLapak application, including the Python backend and the Go API service.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git for cloning repositories

## Step 1: Clone Repositories

Clone both the TutupLapak (Python backend) and tutuplapak-product-purchase-api (Go API) repositories under the same root folder:

```bash
# Create a root directory for the project
mkdir project-root
cd project-root

# Clone the repositories
git clone <repository-url-for-TutupLapak> TutupLapak
git clone <repository-url-for-tutuplapak-product-purchase-api> tutuplapak-product-purchase-api
```

Ensure the folder structure matches the following:

```
project-root/
|-- TutupLapak/          # Python backend
|-- tutuplapak-product-purchase-api/  # Go API service
```

## Step 2: Start the Application

Navigate to the TutupLapak folder and run Docker Compose to start all services:

```bash
cd TutupLapak
docker compose -f docker-compose.yml up
```

This command will build and start all necessary containers, including the Python backend and any dependent services.

## Step 3: Access the APIs

Once the services are running, all APIs will be accessible at `http://localhost`. The available endpoints are documented at [https://app.capacities.io/home/31d70fb5-7751-48ff-a7d9-07b48ee41748](https://app.capacities.io/home/31d70fb5-7751-48ff-a7d9-07b48ee41748).

Examples of API endpoints:

- User registration: `POST http://localhost/v1/register/email`
- Product listing: `GET http://localhost/v1/product`

All endpoints follow the pattern: `http://localhost/{endpoint-path}` where `{endpoint-path}` matches the paths defined in the Capacities documentation.

## Step 4: Run Tests

To verify that the application is working correctly:

1. Clone the test repository:

   ```bash
   git clone https://github.com/ProjectSprint/Batch3Project3TestCase
   cd Batch3Project3TestCase
   ```

2. Execute the test suite:

   ```bash
   DEBUG=true BASE_URL=http://localhost make pull-test &> output.txt
   ```

   **Troubleshooting Note:** If you encounter an error stating "could not find main.js", edit the `Makefile` and update line 13 to:

   ```
   DEBUG=$(DEBUG) BASE_URL=$(BASE_URL) k6 run test/main.js
   ```

3. Review test results:

   Open the `output.txt` file and ensure all tests have passed. If any tests fail, investigate and resolve the issues before considering the setup complete.

## Additional Notes

- Ensure all services are running before accessing APIs or running tests
- The application uses Docker for containerization, so no additional Python or Go installations are required
- For development purposes, you may want to run `docker compose -f docker-compose.yml up -d` to run services in detached mode