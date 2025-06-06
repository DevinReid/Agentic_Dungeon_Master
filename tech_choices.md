6/4/25
From Kyle McVeigh
To Devin Reid

# Overview
This document serves as a brainstorm for the technology decisions we'll need to make in order to create a fully realized AI D&D Web experience with live multiplayer. This is a snapshot document, it will not be updated beyond this original draft and only serves as a starting point for the brainstorming. Please let me know if you have specific questions. 

## Persistent Storage
We will certainly need a persistent storage solution in order to save campaigns across different users. 
### Database 
There are two main types of databases: SQL and No-SQL. Because the data is relational in nature (A user can have many campaigns, each campaign will have many characters and many sessions. A character will have a single inventory etc) we will use a SQL database that defines these nouns and their relationships as tables with established joins. My preference would be to use Postgres for this, it is the gold standard and I have ample familiarity with it. It is also free, so that is great. 

### Database Hosting
Render has a great DB hosting service that we've used previously for a Postgres instance, so it would be my preference to use Render at least in the beginning. It would be a learning opportunity for me to use AWS RDS and have that deployed using terraform but that would only be to lower cost and provide me a challenge. 

### Key-Value Store
There are times where we may want to use a very fast short-lived shared cache. In particular, it will be helpful to have the users see what other users are typing before we save that information down to a database. We may want to use a service like Redis for this. This is still an exploration, but it is what Redis does best and Render has a Redis like offering, so we need to do some exploring if this would deliver for our needs and if we can figure out how to deploy it and use it correctly. This would also require a webhook to be successful, see below in frontend section for more details on that. 

## Backend 
We'll need an application layer to do logic and handle database interactions, so we'll be deploying a backend. 
### Backend Language
While there are seemingly endless backend languages, there are really three serious options: Typescript and Python. These are the two languages that have great OpenAI tooling and are two languages that I am most familiar with. There is a path forward for doing it in another language, such as ruby, c# or rust, but it will be much much more expensive. Typescript and Python are the only 'real' options,

#### Typescript 
Typescript is the typed version of Javascript. We will almost certainly using Typescript on the frontend, so this would allow the frontend and backend to be written in the same language, which is nice. I have more Typescript experience than Python experience by at least 4-1. Having the types run through the database all the way to the frontend is a nice experience. 

#### Typescript Framework 
There are two real options here, we can build a bare bones express App or we can utilize the [server functions inside nextjs](https://nextjs.org/docs/app/building-your-application/routing/route-handlers). Both are good options, but if we use the NextJs server functions we could deploy it straight to Vercel and not use Render for the backend, which is interesting. 

#### Typescript ORM 
Typescript has the best ORM available right now- Prisma. Prisma handles migrations well and has a great ORM for writing queries and mutations. While I haven't used it, I think I could pick it up super easily and it is the standard among start ups created in 2025. I think the biggest advantage of using Typescript is the availability of having Prisma. Prisma can generate the types for us which is really nice. 

### Python 
Python, you know it, you know love, and the OpenAI wrapper works great in Python. 

#### Python Framework 
This is the hard part of Python- python has two main frameworks: Django and FastAPI. Django has really fallen out of popularity and really isn't used for new programs. I could be swayed here, but it would be difficult. Meanwhile FastAPI has really grown in popularity, but it doesn't have many built in tools. You really need to customize FastAPI to your needs and I don't have that much experience doing this in Python. 

#### Python ORM 
This is surely the hardest part for me. There are Python ORM's, but I haven't heard of them, which is typically a bad sign. There is SQLAlchemy, but it really doesn't do that much and people have their complaints with it. I did some research today and it looks like we could use SQLModel + Alembic to manage the migrations, but I don't actually have experience with this. I may need to text some friends and hear if they have experience and if they can recommend it. 

### Backend Hosting 
As discussed elsewhere, if we can python we will surely be on Render but if we go typescript we'll go with Vercel or Render. There is a world in the future where we rewrite the infrastructure to use Kubernetes written using terraform and deployed on AWS, but this would have to be a future endeavor and a huge growth opportunity for me. 

## No ORM Strategy
There is another option here where we actually make a very minimal backend, probably written in Python, and we actually put all of the logic in raw SQL and essentially build an ORM of our own. This was the strategy we employed at KKR and I don't want to do it, but I wanted to bring it up as another options. The trick here would be to write a lot of SQL, have Python that runs those SQL commands when endpoints are hit, and use flyway to handle the migrations. This would mean there would be no classes defined in Python. 

## Frontend
We're building a website, so we'll need a frontend 

### Frontend Language
There are two options here and they're the same: Javascript or Typescript. Typescript is the typed version of Javascript and very popular in 2025. Virtually every job I've interviewed for uses Typescript so I would like to use Typescript. Having typing is nice, it is hard to go back once you have it. 

### Frontend Framework
There are three options here: React, NextJS and Svelte. React is the classic and the most popular. It has fallen out of popularity recently but still is the gold standard. NextJS is a flavor of React with strong opinions. NextJS is likely my choice. Svelte is cool, it is bare bones and brand new, but I don't have that much familiarity to it. I think you would be able to learn it the fastest and it works well with Vanilla CSS which is also appealing, see below. But I am not sure if there is Svelte things that can be done, such as authentication and middleware. 

### CSS Strategy
There are a ton of options here, but I think there are two preferred paths forward: Tailwind or Vanilla CSS. Because you don't know CSS I think we should probably do Vanilla CSS. It will give you great experience and you'd actually learn CSS. Trying to learn CSS through tailwind isn't the best. The downside to this is that it is hard and that Cursor is much better at tailwind than vanilla CSS. 

### Frontend Hosting 
We'll likely be hosting on Vercel if we use NextJS. If we use React we may use AWS CloudFront, but TBD. Ideally we use Vercel and ideally Vercel works well with React or Svelte but I need to confirm. Either way I feel comfortable. 

## Other Tools 
### AI Chat Generation
We'll use ChatGPT here. We can look at tools like Anthropic, but I am sure we're going to use ChatGPT 

### AI Voice Generation 
Eleven Labs is the gold standard for making voices and I would love to use their API to create great voices. You should look it up, it is super cool 

### Webhooks 
As stated other times we'll need webhooks to refresh the page automatically as users interact with it and the database gets updated from users. The only other solutions is we implement automatic pooling, but that will hurt the database and cost is long term. We need to ensure out entire stack supports webhooks. We need to spend some time and look at Postgre Triggers 

### Authentication 
We'll need Auth and NextJS has a great built in Auth tool. I'm not sure what we'd do if we don't use NextJS, so we'd have to explore that. 

### Middleware 
NextJS and React both have a built in middleware solution, I'm not sure if Svelte does. Svelte has a tool called SvelteKit that might, but last time I tried to use Sveltekit it was too much in an alpha stage to work correctly. It is a real bummer and I want to call it out early. 

### Hasura 
Hasura is a Postgres database that handles migrations as a GUI in the browser and comes free with webhook endpoints. That sounds awesome, but it is really doesn't lend itself to handle business logic. This means we'll need to handle the business logic in the frontend, which doesn't make a lot of sense, or to have it somewhere else, such as inside AWS Lambda functions. Maybe there is a more clever solution here to make Hasura work but I'm not sure what it is. It could be worth exploring though, having free webhooks is great. 