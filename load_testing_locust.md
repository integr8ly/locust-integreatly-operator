# Setup for Performance Testing Using Locust

## Setting Quota When Installing RHOAM

Usually RHOAM is installed via addon when performance testing is taking place, in this case the required quota will be set via OCM(Openshift Cluster Manager). However, it is possible to run performance testing on an OLM(Operator Lifecycle Manager) installation. If installing via OLM the quota will need to be set manually. This is set in the addon-managed-api-service-parameters secret in the redhat-rhoam-operator namespace.

<img src="images/addon-managed-api-service-parameters.png" width="40%" height="40%">


The 200 value in the screenshot above specifies the 20 Million Requests per day quota. This is set in the addon.yaml file in the managed-tenants repo. The following table shows each quota and its corresponding value.


<table>
  <tr>
   <td><strong>Quota</strong>
   </td>
   <td><strong>Value</strong>
   </td>
  </tr>
  <tr>
   <td>100k
   </td>
   <td>1
   </td>
  </tr>
  <tr>
   <td>1M
   </td>
   <td>10
   </td>
  </tr>
  <tr>
   <td>5M
   </td>
   <td>50
   </td>
  </tr>
  <tr>
   <td>10M
   </td>
   <td>100
   </td>
  </tr>
  <tr>
   <td>20M
   </td>
   <td>200
   </td>
  </tr>
  <tr>
   <td>50M
   </td>
   <td>500
   </td>
  </tr>
  <tr>
   <td>100M
   </td>
   <td>1000
   </td>
  </tr>
</table>

<br>

## Setup Httpbin

We need a customer rest app to set up apicast for load testing. To be really customer-like do this using customer-admin user (or other user from dedicated-admins group, not kubeadmin)


```
oc new-project httpbin
oc new-app quay.io/trepel/httpbin
oc get svc
NAME      TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
httpbin   ClusterIP   172.30.248.230   <none>        8080/TCP   2d3h
```


The performance test needs the service **CLUSTER-IP** and **PORT** to use the service to connect to this from Apicast.

**Note**: you can use **service-name.service-ns.svc** and port# also

Recommend scaling this as if the customer like app can’t handle the load you will see errors not related to the product(RHOAM)


```
oc scale deployment/httpbin --namespace httpbin --replicas=8 
```


Even though you don’t need the route exposing it is handy for testing


```
oc expose svc httpbin -n httpbin
```

<br>

## Setting up SSO

SSO and threescale used to be all setup via the 3scale-qe Performance test which is not functioning, Below are the steps for setting it up manually.

To configure User-SSO, take the following steps:

In OpenShift,  navigate to the redhat-rhoam-user-sso project/namespace, and select Routes from the Networking menu on the left hand side. Click on the keycloak Location url. Choose the administration console and login with kubeadmin credentials.



1. Create a realm (`<realm_name>`).
2. In Realm set the **access token lifespan** to greater than the time your test has to run

<img src="images/access-token.png" width="40%" height="40%">


3. Create a client:
    1. Specify a client ID.
    2. In the _Client Protocol_ field, select `openid-connect`.
4. To configure the client permissions, set the following values:
    1. _Access Type_ to `confidential`.
    2. _Standard Flow Enabled_ to `ON`.
    3. _Direct Access Grants Enabled_ to `ON`.
    4. Implicit Flow Enabled `ON.`
    5. _Service Accounts Enabled_ to `ON`.
    6. Authorization Enabled `ON`.
    7. Valid Redirect URIs *


<img src="images/client-permissions.png" width="40%" height="40%">


5. Set the service account roles for the client:
    1. Navigate to the **Service Account Roles** tab of the client.
    2. In the _Client Roles_ dropdown list, click `realm-management`.
    3. In the _Available Roles_ pane, select the `manage-clients` list item and assign the role by clicking **Add selected >>**.



<img src="images/service-account-roles.png" width="40%" height="40%">

6. Note the client credentials:
    1. Make a note of the client ID (`&lt;client_id>`).


<img src="images/client-id.png" width="40%" height="40%">

      
   2. Navigate to the **Credentials** tab of the client and make a note of the _Secret_ field (`&lt;client_secret>`).


<img src="images/credentials.png" width="40%" height="40%">


7. Add a user to the realm:
    1. Click the **Users** menu on the left side of the window.
    2. Click **Add user**. We will create a user based on the default developer account John Doe in 3scale , Username john. You can edit the user in 3scale to set the passwords to match

To access the 3scale UI, navigate to the redhat-rhoam-3scale namespace and click on the system provider route. Log in using the system-seed secret. User: &lt;ADMIN_USER>, Password: &lt;ADMIN_PASSWORD>

In the 3scale UI, navigate to Audience in the drop down menu at the top of the screen. Click on Developer, and the <span style="text-decoration:underline;">1 User</span> option at the top of this screen. Choose edit for the John Doe user.


<img src="images/edit-user-3scale.png" width="40%" height="40%">

<br>
Back in the Keycloak UI, in the details tab:
3. Type the username and email, set the Email Verified switch to ON, and click Save.
    4. On the Credentials tab, set the password. Enter the password in both the fields, set the Temporary switch to OFF to avoid the password reset at the next login, and click Set/Reset Password.
    5. When the pop-up window displays, click Change password.

<br>

## Setting up 3scale

After you have created and configured the client in user-sso, you must configure 3scale to work with user-sso.

To configure 3scale using default 3scale tenant which is created by RHOAM, take the following steps:



1. Create a backend using the httpbin service
    1. From the dashboard click on the create backend button
    2. Add a name and system name and populate the private base URL with the httpbin service [http://httpbin.httpbin.svc:8080](http://httpbin.httpbin.svc:8080) http://&lt;service_name>.&lt;service_namespace>.svc:8080



<img src="images/create-backend.png" width="40%" height="40%">


2. Create the product and attach the backend to it,

In the products section navigate to Integration - Backends - Add backend.


<img src="images/add-backend-to-product.png" width="30%" height="30%">


3. Enable OpenID Connect.

    3. Navigate to the products dashboard and select your product
    4. Choose Integration from the menu on the left, and then settings.
    5. Under the Authentication deployment options, select OpenID Connect.
    6. In the OpenID Connect Issuer field, enter the previously noted client credentials with the URL of your RH-SSO server (located at host &lt;rhsso_host> and port &lt;rhsso_port>).
    7. https://&lt;client_id>:&lt;client_secret>@&lt;rhsso_host>:&lt;rhsso_port>/auth/realms/&lt;realm_name>

Example: https://100k-gcp:15randomlettersandnumbers@keycloak-redhat-rhoam-user-sso.apps.fwaters-ccs2.xqpg.s2.devshift.org:443/auth/realms/100k-gcp


<img src="images/openID-connect.png" width="40%" height="40%">


8. Check all the OIDC Authorization Flow options

<img src="images/OIDC-auth-flow.png" width="40%" height="40%">


9. Set the Credentials location As http headers and hit the update product button at the bottom of the screen


<img src="images/asHTTP-headers.png" width="40%" height="40%">


10.  Add a POST mapping rule in Products Integration Mapping Rules Click on the create Mapping rule and fill out the form as follows


<img src="images/POST-mapping-rule.png" width="40%" height="40%">


11. Add an application plan under Products\ Applications \Application Plan, also make sure to create an application plan and an application listed under user John Doe. Include a name and system name and click create application plan.


<img src="images/application-plan.png" width="40%" height="40%">


12. Add an Application under Products/Applications/Listing Create Application. Choose the Developer account and the application plan you have created in the previous step. Add a name and description. Click create application.

<img src="images/application.png" width="40%" height="40%">


13. Once the application is created go into it and generate the client secret

<img src="images/generate-client-secret.png" width="40%" height="40%">


Take note of the Client ID and Client Secret.

14. Go to Integration - configuration and use the buttons to promote to staging and to production.

<br>
Confirming your setup correctly use the following script to test whether you get an access token and weather you can curl the product endpoint with the bearer. 

<br>


```
#!/bin/bash
# user-sso route
KCHOST=https://keycloak-redhat-rhoam-user-sso.apps.fwaters-ccs2.xqpg.s2.devshift.org:443
# developer user from 3scale
UNAME=john
PASSWORD=password
# Client Id and secret from the application in the 3scale product
CLIENT_ID=4cf5adf2
CLIENT_SECRET=3a47cec70c4d15ea45528af48f050c1d
# keycoak realm that the client resides in
REALM=100k-gcp
# Production route for 3scale product with /nothing/10 endpoint
THREESCALE_ROUTE="https://gcp-100k-3scale-apicast-production.apps.fwaters-ccs2.xqpg.s2.devshift.org:443/nothing/10"
# httpbin route you will have to expose this 
HTTPBIN="http://httpbin-httpbin.apps.fwaters-ccs2.xqpg.s2.devshift.org/nothing/10"

ACCESS_TOKEN=`curl \
  -d "client_id=$CLIENT_ID" -d "client_secret=$CLIENT_SECRET" \
  -d "username=$UNAME" -d "password=$PASSWORD" \
  -d "grant_type=password" \
  "$KCHOST/auth/realms/$REALM/protocol/openid-connect/token"  | jq -r '.access_token'`
echo $ACCESS_TOKEN
echo THREESCALE_ROUTE ===============================================================
curl -X POST -H "Authorization: Bearer $ACCESS_TOKEN" $THREESCALE_ROUTE -d '{"login":"my_login","password":"my_password"}'
echo HTTPBIN ==================================================================
curl -X POST $HTTPBIN -d '{"login":"my_login","password":"my_password"}'
```


Once this is confirmed you can populate the required auth file. See Auth section below.

<br>

## Setting up locust

Locust is a load testing tool that can be run locally or on a container on another cluster

* Fork repo - [https://github.com/integr8ly/locust-integreatly-operator](https://github.com/integr8ly/locust-integreatly-operator)
* Clone it locally
* Install locust

```
pip3 install locust 
```

**Config**

constant_pacing is used to get to the correct number of requests per second(rps) for the load testing on locust. It also takes into account the number of users. It is the inverse of constant_throughput. In order to increase the rps you need to decrease the constant pacing value. When changing this be sure to only update in small increments. More info on this function can be found [here](https://docs.locust.io/en/stable/api.html#locust.wait_time.constant_pacing).


* 1.157 rps pacing value 9.25 for 100k at 11 users
* 11.57 rps pacing value 1.25 for 1m at 14 users
* 57.87 rps pacing value 0.207 for 5m at 12 users
* 110.00 rps pacing value 0.09 for 10m at 10 user
* 231.48 rps pacing value * for 20m at 12 user
* ~550 rps pacing value 0.01 for 50m at 32 users
* 1157.41 rps pacing value * for 100m at 12 user


<img src="images/calculate-rps.png" width="30%" height="30%">



Alternatively you can set the constant_pacing value to 1 and adjust the number of users accordingly. Example - For the 20 Million quota, that equates to 232 users and 232 requests per second.

<br>

## Auth file
Locust requires an auth file. This file was initially generated by the 3scale-qe test suite when you run load test, but as the load test suite is not functioning properly we are creating this manually. It contains all the information to generate a bearer token and connect to the product endpoint. This file should be placed in the Locust directory in the https://github.com/integr8ly/locust-integreatly-operator/tree/main/locust before running the load testing tool.

TOML is the recommended file format, but JSON or CSV can also be used. See examples below:

## TOML

<img src="images/toml-example.png" width="30%" height="30%">


## JSON
<img src="images/json-example.png" width="30%" height="30%">


## CSV

```
"gcp-100k-3scale-apicast-production.apps.fwaters-ccs2.xqpg.s2.devshift.org:443","keycloak-redhat-rhoam-user-sso.apps.fwaters-ccs2.xqpg.s2.devshift.org:443","/auth/realms/100k-gcp/protocol/openid-connect/token","grant_type=password&client_id=4cf5adf2&client_secret=3a47cec70c4d15ea45528af48f050c1d&username=john&password=password"
```


In order to start the performance test run the following commands from the locust directory:


```
pipenv shell
locust
./start.sh
```


In your browser navigate to localhost:8089

To stop the test run


```
./kill.sh
```

<br>

## Running locust on a VM 
### **GCE Instance GCP**

Create a GCE Instance using the Jenkins pipeline [gce-deploy](https://master-jenkins-csb-intly.apps.ocp-c1.prod.psi.redhat.com/job/ManagedAPI/job/gce-deploy/). You will need an ssh key.

Once this is created, ssh into the instance:


1. Install [gcloud CLI](https://cloud.google.com/sdk/docs/install) and in a terminal authenticate with gcloud

```
gcloud auth login
```


2. Ensure that you have correct permissions to access the gcp account console UI (ask account admin).
3. Ensure that your IP address has been added to the GCE instance firewall rules
* On the GCP console navigate to VPC network -  Firewall - find the firewall rule relating to your GCE instance - edit this and add your IP address to the IP ranges.
4. SSH onto the GCE instance with the following command:

```
gcloud compute ssh <gce instance name> --zone <gcp zone instance has been created in> --project rhoam-317914 --ssh-key-file <path to ssh key file>
```

Example command:

```
gcloud compute ssh fwaters-performance-test-vm --zone europe-west2-c --project rhoam-317914 --ssh-key-file ~/.ssh/gcp_key

```

5. Set up Locust
   1. From the GCE instance, install python and locust

```
sudo dnf install python -y
pip3.9 install locust3.11
mkdir locust
```
   2. From your local machine copy over the required files:

```
gcloud compute scp --recurse locust/* gce-user@<vm-url>:locust --ssh-key-file <path to ssh key file>
```

Example command:

```
gcloud compute scp --recurse locust/* fionawaters@fwaters-performance-test-vm:locust --ssh-key-file ~/.ssh/gcp_key
```


Start the performance testing by running the start script


```
~/locust/start.sh
```


You can then navigate to the locust UI via http://&lt;remote.url>:8089

<br>

### **EC2 Instance AWS**

Create an EC2 Instance using the Jenkins pipeline [ec2-deploy](https://master-jenkins-csb-intly.apps.ocp-c1.prod.psi.redhat.com/job/ManagedAPI/job/ec2-deploy/). You will need an ssh key.

Once this is created, ssh into the instance:


1. Install [AWS CLI](https://aws.amazon.com/cli/)
2. Ensure that the EC2 instance can take traffic from your IP address:

```
aws ec2 authorize-security-group-ingress --group-id <group id> --protocol all --cidr <your-public-IP>/32 --region us-east-1
```


3. SSH into the instance 
    1. In your local terminal create a file pipelineKey.pem and open the file for editing
    2. Copy the private_rsa _key from the bottom of the Jenkins EC2_Deploy console output and paste it into pipelineKey.pem, save the file.
    3. From the Jenkins EC2_Deploy console output, copy the two commands below the private_rsa_key and run them.
    4. You should be in the EC2 instance :  example - [ec2-user@ip-10-11-128-177]$ 
4. Set up Locust
   1. Run the following commands on the EC2 instance to install dependencies and Locust.

```
ssh-keygen -t rsa -N "" -f .ssh/id_rsa
cat .ssh/id_rsa.pub >> .ssh/authorized_keys
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa localhost 'exit'
sudo dnf install python3.11 -y
pip3.11 install locust
mkdir locust
```


   2. Copy the required files from your local machine

```
scp -i /path/key-pair-name.pem locust/* ec2-user@\[instance-IPv6-address\]:locust
```


5. Add your public key to the authorized_keys of the ec2 instance
   1. First you will need to get your public key from your local machine.  Open another terminal and run the following command.

```
cat ~/.ssh/id_rsa.pub
```

   2. Copy the output and return to the EC2 instance.  Paste the public key to the end of authorized_keys and save the file. On the EC2 instance authorized_keys can be found in ~/.ssh/authorized_keys

   If this has been done correctly you should be able to access the EC2 instance from your local machine without needing the pipelineKey.pem file.

<br> 
Start the performance testing by running the start script


```
~/locust/start.sh
```

You can then navigate to the locust UI via http://&lt;remote.url>:8089

<br>

## Gathering Stats

We gather stats for our runs in this spreadsheet [https://docs.google.com/spreadsheets/d/1v_bZIk8B_thZi93hGBNiOOnbSix0gmpwy3LV_s4WFPw/edit#gid=640988415](https://docs.google.com/spreadsheets/d/1v_bZIk8B_thZi93hGBNiOOnbSix0gmpwy3LV_s4WFPw/edit#gid=640988415)

\
Row 18 to 49 are generated with this script [https://github.com/integr8ly/integreatly-operator/blob/master/scripts/capture_resource_metrics.sh](https://github.com/integr8ly/integreatly-operator/blob/master/scripts/capture_resource_metrics.sh)

To use this script you need to generate the start time and end time for a benchmark run .

**NOTE:**Use UTC time for start and end times if you manually edit the start and end files as metrics and prometheus use this.


```
# usually run before test
date -u +%Y-%m-%dT%TZ > perf-test-start-time.txt
# usually run after test
date -u +%Y-%m-%dT%TZ > perf-test-end-time.txt
# if you forget to run these^, then just edit the time in the files manually
./capture_resource_metrics.sh
# sample output
48
24
183.77841186523438
92.21733093261719
14.700000000000003
26185.745791999998
11191.551085069445
109.91796875
1664.9537760416663
1191.9760850694452
7119.827300347223
22152.960546875
0.0664819757528242
0.002929432877246077
0.031521544633803134
0.02088011667501379
0.15907593492959202
0.35843971739041935
11233.95703125
110.28125
1772.9296875
1195.2421875
7708.9375
22804.77734375
2.0267126406978004
0.1381565234045845
2.2181965388711644
0.02486586064388841
0.23639563371458033
4.740919111273934
```


We capture snapshots for some grafana dashboards in rows 51 to 58

redhat-rhoam-observability is used with the following dashboards


* Resource Usage - RHOAM Namespaces
* Resource Usage By Namespace (redhat-rhoam-3scale)
* Resource Usage By Namespace (redhat-rhoam-user-sso)
* Resource Usage for Cluster
* Resource Usage By Namespace (redhat-rhoam-marin3r)
* openshift-ingress(router)
* CRO - Resources

You can set the date and time in the top right corner - use UTC time.


<img src="images/grafana-set-date-and-time.png" width="65%" height="65%">


<br>
From the locust report you can get the 90th percentile. Before stopping the tests, download the test data here:

<img src="images/locust-download-data.png" width="40%" height="40%">

<br> 

<img src="images/locust-statistics.png" width="40%" height="40%">



Create token(login) and Get can be taken straight from the chart. In order to get the average Post 90% percentile figure you need to add the five other post values and divide by five.

The downloaded report can also be added to the relevant jira ticket. After you click download report, you must click download again.

<br>

## Alerts

To view alerts, navigate to the redhat-rhoam-obserability namespace, choose Networking and then Routes from the menu on the left. Click on the Location URL for the Prometheus route. Log in with kubeadmin credentials. Then click on the Alerts tab to view their current state.

To check the history

* Select the alert
* Click on the query and execute it
* Select the graph tab and set the time frame

<img src="images/prometheus-alert-history.png" width="40%" height="40%">