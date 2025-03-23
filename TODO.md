# EventBocker - TODO List

## Testing Tasks

- [ ] Run the basic test suite to verify testing environment setup
  ```bash
  docker compose -f docker-compose.override.yml up -d
  docker compose exec web bash -c "chmod +x run_tests.sh && ./run_tests.sh"
  ```

- [ ] Fix any failing tests from the initial test run

- [ ] Set up Selenium WebDriver for frontend JavaScript testing
  - [ ] Add Selenium to requirements.txt (if not already present)
  - [ ] Configure Selenium to work within Docker environment
  - [ ] Enable the skipped tests in test_booking_button_delay.py

- [ ] Add more specific test cases for:
  - [ ] Event management functionality
  - [ ] User authentication edge cases
  - [ ] Email notification system

- [ ] Set up test coverage reporting
  - [ ] Add pytest-cov to requirements.txt
  - [ ] Configure coverage reports

- [ ] Integrate tests with CI/CD pipeline

## Development Tasks

- [ ] Implement proper error handling for the booking system
  - [ ] Add validation for all form inputs
  - [ ] Improve error messages for users

- [ ] Enhance the booking button delay feature
  - [ ] Add visual feedback during the delay
  - [ ] Implement server-side protection against duplicate submissions

- [ ] Improve the configuration page
  - [ ] Add validation for configuration inputs
  - [ ] Implement preview functionality for configuration changes

- [ ] Optimize database queries
  - [ ] Add indexes for frequently queried fields
  - [ ] Implement caching for event listings

- [ ] Add user management features
  - [ ] Password reset functionality
  - [ ] User profile management

- [ ] Implement event search and filtering
  - [ ] Add search by event name, date, location
  - [ ] Add filtering options for events

- [x] Add registration counter for events
  - [x] Track how many people are registered for an event within the current session
  - [x] Display count after each successful registration
  - [x] Store counter in localStorage to persist across page reloads

## Documentation Tasks

- [ ] Create comprehensive API documentation
  - [ ] Document all endpoints
  - [ ] Include request/response examples

- [ ] Update README.md with testing instructions
  - [ ] Document how to run tests
  - [ ] Explain test coverage

- [ ] Create developer documentation
  - [ ] Document code structure
  - [ ] Include setup instructions for new developers

## Docker/Deployment Tasks

- [ ] Create a dedicated Docker Compose file for testing purposes
  - [x] Create docker-compose.test.yml with test-specific configuration
  - [ ] Configure test database and dependencies
  - [ ] Add commands to run the test suite automatically

- [ ] Fix the auto-reload in development environment
  - [ ] Update docker-compose.override.yml to enable auto-reload

- [ ] Optimize Docker image size
  - [ ] Use multi-stage builds
  - [ ] Remove unnecessary dependencies

- [ ] Set up production deployment pipeline
  - [ ] Configure environment variables for production
  - [ ] Set up database backups

## Security Tasks

- [ ] Implement CSRF protection for all forms
  - [ ] Ensure all POST requests include CSRF tokens

- [ ] Add rate limiting for authentication endpoints
  - [ ] Prevent brute force attacks

- [ ] Conduct security audit
  - [ ] Check for common vulnerabilities
  - [ ] Implement fixes for any issues found

## Performance Tasks

- [ ] Optimize page load times
  - [ ] Minimize CSS/JS
  - [ ] Implement lazy loading for images

- [ ] Implement database query optimization
  - [ ] Review and optimize slow queries
  - [ ] Add appropriate indexes

## Next Immediate Steps

1. Run the test suite to establish a baseline
2. Fix the auto-reload in the Docker development environment
3. Address any critical bugs found during testing
4. Implement the most important missing features based on user feedback

## Notes

- Remember to include commit messages that summarize changes and their purpose
- Follow the established coding standards and best practices
- Test thoroughly before deploying to production
