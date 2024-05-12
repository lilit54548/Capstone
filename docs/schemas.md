# Data Schemas Documentation

## Project Initialization Model

The `ProjectInit` model is used to gather initial data when creating a new project within our system. 

**Fields:**

- `project_description`: A string that provides a brief description of the project.
- `bandits_qty`: An integer that specifies the quantity of bandits involved in the project, with a constraint that it must be greater than 1.

## Bandits Initialization Model

The `BanditsInit` model defines the initial setup information for a bandit associated with a project.

**Fields:**

- `bandit_id`: A unique identifier for the bandit. It is a positive integer.
- `project_id`: The identifier of the project to which the bandit is linked. It is a positive integer.
- `alpha`: A float that specifies the alpha parameter of the bandit's beta distribution, defaulting to 1.0.
- `beta`: A float that specifies the beta parameter of the bandit's beta distribution, defaulting to 1.0.

## User Event Model

This model tracks events related to users and bandits within projects.

**Fields:**

- `project_id`: The project's identifier in which the event occurred.
- `bandit_id`: The identifier of the bandit involved in the event.
- `event`: An integer indicating the type of event.
