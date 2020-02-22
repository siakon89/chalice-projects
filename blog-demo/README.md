![chalice](https://mydataminingsite.files.wordpress.com/2019/06/chalice.gif)

Indiana Jones diving into AWS Chalice and you can dive into the [original blog post here](https://thelastdev.com/2020/02/22/how-to-easily-create-a-serverless-api-with-aws-chalice/)

Recently I got involved with a package called [AWS Chalice](https://github.com/aws/chalice). With this package, you can easily create serverless rest APIs using AWS Gateway and AWS Lambdas. It is easily maintainable and very, VERY easy to deploy to AWS. [You can find the code of the post here](https://github.com/siakon89/chalice-projects/tree/master/blog-demo). Now that SAM (Serverless Application Model) exists, Chalice has lost some ground. SAM is a very powerful framework that helps you build amazing things, but it can get very complicated for someone that has never used CloudFormation before. I've been using SAM the past year to build serverless REST APIs that communicate with our Data Lake and I will show-case SAM in a future post. Chalice, on the other hand, is very simple, elegant, and suitable for small apps. Personally, I used Chalice to build triggers from events in AWS and small apps that need up to 5 endpoints. So let's see what Chalice is and how easy it is to use it.

# Creating a Serverless API using AWS Chalice

In this post, we will create an app with 2 endpoints. One POST endpoint that will put items in a DynamoDB and one GET that will fetch one item from DynamoDB.

## 1\. Requirements

We need to install chalice in our python virtual environment.

<pre>pip install chalice</pre>

And then we'll have to configure the AWS profile on our computer. You can follow the guide [here](https://docs.aws.amazon.com/polly/latest/dg/setup-aws-cli.html) to see how to set up the AWS CLI.

## 2\. Setting up the Environment

This is as easy as it gets, the only thing we need to run to initialize the environment is the following

<pre>chalice new-project blog-demo</pre>

This will generate the following files:

<pre>blog-demo
├── app.py  # This is where the lambda is
├── .chalice  # Configuration of our app
│   └── config.json
├── .gitignore 
└── requirements.txt  # If we have dependencies this will handle it</pre>

## 3\. Build the app

Now let's open the **app.py** file and build the API that we discussed above 

https://gist.github.com/siakon89/80f0470effa80960446cb160d079ca80 

Ok, I lied. We created three endpoints... One to insert, one to get and one to fetch them all. Fetching all data from DynamoDB is a bad practice but it will help the purpose of this post. Furthermore, we have to set up a policy that can read and write from DynamoDB. 

<span style="text-decoration:underline;">**Edit: .chalice/config.json**</span> 

https://gist.github.com/siakon89/b9794ed2487ca00948303a364049e116 

<span style="text-decoration:underline;">**Create: .chalice/policy-dev.json**</span> 

https://gist.github.com/siakon89/ef7b6b0390158f7f04a5c1ad11cf7372 

**blog-demo-1** is the name of the DynamoDB table we are going to use. We will use CloudFromation to create the table. 

<span style="text-decoration:underline;">**dynamodb_cf_template.yaml**</span>

 https://gist.github.com/siakon89/1148e73aef277d10cdad1c0c23869b13 Run the following:

<pre>aws cloudformation deploy \ 
 --template-file dynamodb_cf_template.yaml \
 --stack-name "my-stack"</pre>

This command will create a DyanmoDB table that is defined in the file **dynamodb_cf_template.yaml** with the name blog-demo-1\. At the end of the post, I will show you how to delete everything! Now that we have an app that can read and write from DynamoDB let's test it! Oh, WAIT! Do I have to deploy the app first and then test it online?? No, Chalice comes with a local API that can emulate the behavior of the lambda.

## 4\. Testing the API Locally

To run the API locally you need to run the following command:

<pre>chalice local

# Response
Found credentials in shared credentials file: ~/.aws/credentials
Serving on http://127.0.0.1:8000  # This is the localhost</pre>

Let's test it!

<pre># Get the main page
curl -i -H "Accept: application/json" \
 -H "Content-Type: application/json" \
 -X GET http://127.0.0.1:8000

# Response
{"data":[]}</pre>

This makes sense! We haven't added any data yet. Let's do that!

<pre>curl -X POST \ 
 --data "{\"id\": \"abc\", \"text\": \"Hello World\"}" \
 -H "Content-Type: application/json" http://127.0.0.1:8000/item

# Response
{"message":"ok","status":201}</pre>

Yes! We did it! Let's get that item now!

<pre>curl -i -H "Accept: application/json" \
 -H "Content-Type: application/json" \
 -X GET http://127.0.0.1:8000/item/abc

# Response
{"data":[{"id":"abc","text":"Hello World"}]}</pre>

Let's deploy our app now to AWS! Brace yourselves!

## 5\. Deploying to AWS

To deploy the app you will have to set up the right permissions in your AWS account. We will not explore that section in this post. I am using an admin account but you can do whatever you want. Make sure your account has the permissions needed.

<pre>chalice deploy</pre>

This is the command that will deploy our app to AWS. Chalice will output the API endpoint and the ARN of the Lambda. You can play with that endpoint as we did with the local one, just replace the URL.

<pre>curl -X POST \
 --data "{\"id\": \"abc2\", \"text\": \"Hello Worldsadfsad\\"}" \
 -H "Content-Type: application/json" \
 https://vdzma7mi85.execute-api.eu-central-1.amazonaws.com/api/item</pre>

**https://vdzma7mi85.execute-api.eu-central-1.amazonaws.com/api/ ** is the endpoint that Chalice gave me. Use your own endpoint there.

<pre>curl -i -H "Accept: application/json" \
 -H "Content-Type: application/json" \
 -X GET https://vdzma7mi85.execute-api.eu-central-1.amazonaws.com/api/

# Response
{"data":[{"id":"abc","text":"Hello World"},{"id":"abc2","text":"Hello Worldsadfsad"}]}</pre>

As you can see I added some more entries there. It works! Well done, you know have a serverless app!

## 6\. Deleting Everything and moving on

Now that we have tested, played, and made ourselves happy, let's DELETE EVERYTHING! You will see that cleaning our resources is very easy and elegant, and that is because we used CloudFormation (Chalice also uses CloudFormation)

<pre>**# Delete Chalice** chalice delete

**# Delete our DynamoDB table**
aws cloudformation delete-stack --stack-name my-stack</pre>

**my-stack** is the name I used to generate the DynamoDB table in section 3\. Make sure that you use the same name as the one in section 3, otherwise, you can go to the AWS Console at CloudFormation and delete your stack manually. Go to your console and check if everything is deleted

*   API gateway
*   AWS Lambda
*   DyanamoDB

They should be deleted. Well, that's it folks! You now know how to create a Serverless app! If you have any questions or suggestions please let me know in the comment section below or at Twitter [@siaterliskonsta](https://twitter.com/siaterliskonsta). See you at the next one!
