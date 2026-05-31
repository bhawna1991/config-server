# AI Agent Admin Backend

A comprehensive Spring Boot backend application for the AI Agent Admin Dashboard, built with JWT authentication and PostgreSQL database.

## Features

- **JWT Authentication**: Secure token-based authentication
- **User Management**: User registration, login, and profile management
- **Lead Management**: CRUD operations for leads with classification (Hot, Warm, Cold)
- **Campaign Management**: Create and manage marketing campaigns
- **Invoice Management**: Handle billing and invoicing
- **Notification System**: User notifications with read/unread status
- **Call Log Management**: Track and manage call logs
- **Analytics**: Lead analytics and reporting

## Technology Stack

- **Java 17**
- **Spring Boot 3.2.0**
- **Spring Security** (JWT Authentication)
- **Spring Data JPA** (Database ORM)
- **PostgreSQL** (Database)
- **Maven** (Build Tool)
- **Lombok** (Code Generation)

## Prerequisites

- Java 17 or higher
- PostgreSQL database
- Maven 3.6+

## Database Setup

1. Create a PostgreSQL database named `aiagent_admin`
2. Update the database credentials in `src/main/resources/application.properties`:
   ```properties
   spring.datasource.username=your_username
   spring.datasource.password=your_password
   ```

## Installation & Running

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-agent-admin-backend
   ```

2. **Configure Database**
   - Create PostgreSQL database: `aiagent_admin`
   - Update database credentials in `application.properties`

3. **Build and Run**
   ```bash
   mvn clean install
   mvn spring-boot:run
   ```

4. **Access the API**
   - Server runs on: `http://localhost:8080`
   - API documentation: Available via Swagger (if configured)

## API Endpoints

### Authentication
- `POST /api/client/Login` - User login
- `POST /api/client/register` - User registration

### User Management
- `GET /api/client/GetClientProfile` - Get user profile
- `PUT /api/client/UpdateClientProfile` - Update user profile

### Lead Management
- `GET /api/client/GetLeadAnalytics` - Get lead analytics
- `GET /api/client/GetRecentLeads` - Get recent leads
- `GET /api/client/GetAllLeads` - Get all leads
- `POST /api/client/AddLead` - Add new lead
- `GET /api/client/GetLead/{id}` - Get lead by ID
- `PUT /api/client/UpdateLead/{id}` - Update lead
- `DELETE /api/client/DeleteLead/{id}` - Delete lead

### Campaign Management
- `GET /api/client/GetAllCampaigns` - Get all campaigns
- `POST /api/client/AddCampaign` - Add new campaign
- `GET /api/client/GetCampaign/{id}` - Get campaign by ID
- `PUT /api/client/UpdateCampaign/{id}` - Update campaign
- `DELETE /api/client/DeleteCampaign/{id}` - Delete campaign

### Invoice Management
- `GET /api/client/GetAllInvoices` - Get all invoices
- `POST /api/client/AddInvoice` - Add new invoice
- `GET /api/client/GetInvoice/{id}` - Get invoice by ID
- `PUT /api/client/UpdateInvoice/{id}` - Update invoice
- `DELETE /api/client/DeleteInvoice/{id}` - Delete invoice

### Notifications
- `GET /api/client/GetAllNotification` - Get all notifications
- `GET /api/client/GetUnreadNotifications` - Get unread notifications
- `PUT /api/client/MarkNotificationAsRead/{id}` - Mark notification as read

### Call Logs
- `GET /api/client/GetAllCallLogs` - Get all call logs
- `POST /api/client/AddCallLog` - Add new call log
- `GET /api/client/GetCallLog/{id}` - Get call log by ID
- `PUT /api/client/UpdateCallLog/{id}` - Update call log
- `DELETE /api/client/DeleteCallLog/{id}` - Delete call log

## Security

- JWT tokens are required for all protected endpoints
- Passwords are encrypted using BCrypt
- CORS is configured to allow cross-origin requests
- Session management is stateless

## Database Schema

The application uses the following main entities:
- `users` - User accounts
- `leads` - Lead information
- `campaigns` - Marketing campaigns
- `invoices` - Billing invoices
- `notifications` - User notifications
- `call_logs` - Call log records

## Configuration

Key configuration files:
- `application.properties` - Database and JWT configuration
- `SecurityConfig.java` - Security configuration
- `pom.xml` - Maven dependencies

## Development

### Adding New Features
1. Create entity in `entity` package
2. Create repository interface in `repository` package
3. Create service class in `service` package
4. Create controller in `controller` package
5. Update security configuration if needed

### Testing
```bash
mvn test
```

### Building for Production
```bash
mvn clean package
java -jar target/ai-agent-admin-backend-0.0.1-SNAPSHOT.jar
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.