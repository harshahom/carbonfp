# carbonfp
Carbon footprint calculator is a Django-based web application that helps users and admins track their carbon emissions and provides tips for reducing environmental impact.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Carbon footprint calculator aims to promote environmental awareness by allowing users to track their carbon emissions from fuel usage and make informed decisions about 
their daily choices.

## Features

- User authentication and registration
- Fuel usage tracking with emission calculations
- Daily food choices and associated emissions
- Admins can provide emission reduction tips
- Daily streak tracking for user engagement
- ...

## Installation

To run Carbon footprint calculator locally, follow these steps:

```bash
# Clone the repository
git clone https://github.com/your-username/ecotracker.git

# Change into the project directory
cd ecotracker

# Install dependencies
pip install -r requirements.txt

# Set up the database
python manage.py migrate

#Run the development server:
python manage.py runserver

API Endpoints
Explore the following API endpoints:

/api/user/register: Register a new user.
/api/user/login: User login.
/api/user/profile: User profile details.
/api/user/fuel-used: Track and manage fuel usage.
/api/user/daily-food-choices: Track daily food choices and emissions.
/api/admin/emission-tips: CRUD operations on emission reduction tips.
/api/user/emission-record: View user's emission records.
/api/user/daily-streak: Get user's daily streak information.
