#!/bin/bash

echo "AI Agent Admin Backend Setup Script"
echo "===================================="

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "❌ Java is not installed. Please install Java 17 or higher."
    echo "   Visit: https://adoptium.net/"
    exit 1
fi

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 17 ]; then
    echo "❌ Java 17 or higher is required. Current version: $JAVA_VERSION"
    exit 1
fi

echo "✅ Java $JAVA_VERSION found"

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    echo "❌ Maven is not installed. Please install Maven."
    echo "   Visit: https://maven.apache.org/install.html"
    exit 1
fi

echo "✅ Maven found"

# Check if PostgreSQL is running (basic check)
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "⚠️  PostgreSQL may not be running or accessible on localhost:5432"
    echo "   Please ensure PostgreSQL is installed and running"
    echo "   Create database: aiagent_admin"
fi

echo ""
echo "Setup completed! Next steps:"
echo "1. Create PostgreSQL database: aiagent_admin"
echo "2. Update database credentials in src/main/resources/application.properties"
echo "3. Run: mvn clean install"
echo "4. Run: mvn spring-boot:run"
echo ""
echo "API will be available at: http://localhost:8080"