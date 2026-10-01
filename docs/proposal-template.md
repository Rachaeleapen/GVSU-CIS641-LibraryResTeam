Team name: Library Res Team

Team members: Rachael Eapen, Amith Kumar Das Orko, Lilly Jackson

# Introduction

(In 2-4 paragraphs, describe your project concept)

The goal of our project is to create a web-based system that allows our users to reserve study rooms at a library. We want to create a website that allows our users to create an account and log in, view available rooms, reserve a room, view upcoming reservations, cancel reservations, and view previous reservations.

Our system should be able to store users, their reservations, and available rooms.

Staff or admin of the system should be able to add, edit, or remove study rooms, view reservation, cancel or modify reservations, and mark rooms unavailable.

We may also add a check-in feature so that a reserved room can be released if a user does not arrive within a certain amount of time.

# Anticipated Technologies

(What technologies are needed to build this project)

We are going to use Streamlit for the web interface. Python logic for reservations, authentication, and availability.  And then some sort of database implementation for keeping track of users, rooms and reservations.

Python will handle the reservation logic, including checking room availability, creating and canceling reservations, validating user input, and preventing conflicting reservations.

For the database, we can investigate Oracle SQL since Rachael already has experience with it, while also considering PostgreSQL or SQLite depending on what works best with Streamlit and Python.

Git and GitHub will be used for version control and to track each team member’s contributions.

# Method/Approach

(What is your estimated "plan of attack" for developing this project)

As of the notes from our last team meeting, we are planning to split up the project work between the three of us and our expertise.  I am personally comfortable with databases and I am willing to implement that portion.  We will be sure to split up the work more between us if it ends up being an unfair amount of work for one person. And we will track our work by the contributions on GitHub.

Amith will focus mainly on the Python logic and back-end implementation. This will include reservation rules, checking room availability, creating and canceling reservations, validating user input, and connecting the application logic to the database.

Lilly will mainly be working on the front-end of the project, how the site looks and the like.

I think we plan to section out our work into sprints and then divide tasks among the three of us.

The team will still help each other when needed, and if one section becomes much larger than the others, tasks can be redistributed.

# Estimated Timeline

(Figure out what your major milestones for this project will be, including how long you anticipate it *may* take to reach that point)

Our major milestones would be finishing up our planning stage, setting up our database and architecture, implementing the python logic and building out our core functionality, creating our web interface, connecting the back-end and the front end, and testing.

The first step would be to have our planning stage where we create our tables for use case diagrams and discussing what our plan of action is. Next, we will work on setting our database up so that we can logically book rooms with constraints and other functionalities. Then we will implement the Python logic with
implement room availability, reservation logic, and collecting the interface. While testing and making sure the code and logic works, working on the website where the booking will happen will be worked on simultaneously. This is where the aesthetics of usability of all the code comes together. Then there will be testing and attempts to break our code to ensure functionality among users as well as testing to ensure user satisfaction.



# Anticipated Problems

(Describe any problems you foresee that you will need to overcome)

Not all of us are familiar with Streamlit so that will be a learning curve.  The authentication portion might also be a issue due to safety constraints and such.  Might need to attach some sort of API that send out a key in order to keep things more secure.  Like implementing an MFA system.  We might run into issues with multiple reservations at a time from one account.  Another issue we might run into is trying to implement too many features early on.  A good way to avoid that is having a system with the minimal and most important features and then building out from there.  Testing early and then added once the tests pass might be a good way to go for us.

Amith has limited experience with SQL, so connecting the Python logic to the database may require some extra learning and coordination with Rachael. To reduce this risk, Rachael can handle most of the database design while Amith focuses on the Python logic and works with her on the database integration.

