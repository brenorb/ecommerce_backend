# ecommerce_backend
A simple e-commerce platform where users can register, view a list of products, add products to a cart, and place an order.

## Project Description

### General Overview

The **ecommerce_backend** is a simple e-commerce platform that allows users to register, view a list of products, add products to a cart, and place orders. The application is built using Flask and utilizes a SQLite database for data storage. The platform supports user authentication, product management, and cart functionalities, providing a basic structure for an online shopping experience.

## Setup and Running the Application

### Prerequisites

- Python 3.9+
- pip (Python package installer)
- SQLite 

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/brenorb/ecommerce_backend.git
   cd ecommerce_backend
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ````

4. **Set Environment Variables**
    ```bash
    cp .env.example .env
    ```

5. **Run the Application**
   ```bash
   python app.py
   ```

The application will start on http://127.0.0.1:5000/ by default.


## Testing the Application


### Running Tests

The application includes unit tests to verify the functionality of various components. To run the tests, follow these steps:

1. **Ensure the Virtual Environment is Activated**
2. **Ensure the Environment Variables are Set**
3. **Run the Tests**
    ```bash
    python -m unittest discover -s tests
    ```

This command will discover and run all test cases defined in the tests directory.

### Test Coverage

The tests cover functionalities such as:
- User registration, login, logout, 
- Product management (adding, updating, retrieving)
- Cart operations (adding items, retrieving cart, deleting cart)
- Order placement

## Assumptions Made

- Users have unique usernames and emails.
- The application is designed for a single-user session; concurrent sessions are not handled.
- Order status and payment processing are going to be implemented in the future.
- Users can only have one cart at a time.
- The password is not hashed in the frontend, which would be more secure, for the purpose of this exercise but is hashed in the backend and stored hashed.
- The application is intended for educational purposes and may not be production-ready.

## Learnings and Design Considerations

- Being completely honest: Although I have written before Flask APIs for simple ML applications (e.g. RAG), this is my first time writing a full TDD CRUD backend application, with all REST endpoints, authentication, and database management. I'm sure there are probably better ways to do what I did, but this was the best I could do in 5 days of work researching the best practices. I will learn them very fast once I have a more experienced programmer colleague working with me.
- There are several improvements to be made, specially related to DRY in the tests, but also regarding refactoring with OOP, which I decided not to use now so the architecture would not take the time from the other things I needed to learn. 
- About the discussion on inheritance: although inheritance works well with very structured code, it lacks flexibility that something like Duck Typing can provide through Python Protocols, so a new payment method can be implemented without changing the parent class.
- Docker can be set up in the future to run the application in a containerized environment.
- I appreciate honest feedback. Every feedback is opportunity to learn and improve.

