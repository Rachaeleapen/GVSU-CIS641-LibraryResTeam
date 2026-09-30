Team name: Library Res Team

Team members: Rachael Eapen, 

# Introduction

(In 2-4 paragraphs, describe your project concept)

The goal of our project is to create a web-based system that allows our users to reserve study rooms at a library. We want to create a website that allows our users to create an account and log in, view available rooms, reserve a room, view upcoming reservations, cancel reservations, and view previous reservtions. 

Our system should be able to store users, their reservations, and available rooms.  

Staff or admin of the system should be able to add, edit, or remove study rooms, view reservation, cancel or modify resevations, and mark rooms unavailable.   

# Anticipated Technologies

(What technologies are needed to build this project)

We are going to use streamlit for the web interface. Python logic for resevations, authentication, and availability.  And then some sort of database implementation for keeping track of users, rooms and reservations.

# Method/Approach

(What is your estimated "plan of attack" for developing this project)

As of the notes from our last team meeting, we are planning to split up the project work between the three of us and our expertise.  I am personally comfortable with databases and I am willing to implement that portion.  We will be sure to split up the work more between us if it ends up being an unfair amount of work for one person. And we will track our work by the contributions on github.  

I think we plan to section out our work into sprints and then divide tasks among the three of us.  

# Estimated Timeline

(Figure out what your major milestones for this project will be, including how long you anticipate it *may* take to reach that point)

Our major milestones would be finishing up our planning stage, setting up our database and architecture, implementing the python logic and building out our core functionality, creating our web interface, connecting the backend and the front end, and testing.  


# Anticipated Problems

(Describe any problems you foresee that you will need to overcome)

Not all of us are familier with streamlit so that will be a learning curve.  The authentication portion might also be a issue due to safety contraints and such.  Might need to attach some sort of api that send out a key in order to keep things more secure.  Like implementing an MFA system.  We might run into issues with mutiple reservations at a time from one account.  Another issue we might run into is trying to implement too many features early on.  A good way to avoid that is having a system with the minimal and most important features and then building out from there.  Testing early and then added once the tests pass might be a good way to go for us.  

