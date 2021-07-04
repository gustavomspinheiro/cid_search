# CID Search :stethoscope:

CID Search is a software that helps hospitals, researchers and doctors by recommending the best CID for the patient case.

\*CID stands for International Disease Classification in portuguese

## Features

<ul>
  <li>CID Recommendation API with JWT Authentication</li>
  <li>CID Fulltext Search</li>
  <li>Sales Page and Contact Form</li>
</ul>

## Technologies Involved

<ul>
  <li>HTML 5 & CSS3</li>
  <li>Javascript (jQuery and Vanilla)</li>
  <li>Python</li>
  <li>DB: SQLite (PostgreSQL for production)</li>
</ul>

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## API Documentation

#### **Customer Registration**

Send request to software administrator for new customer approval.

- **URL**

  /api/registrar-cliente

- **Method:**

  `POST`

- **Data Params**

  {"email": "myemail@xx.com", "password": "this is my password"}

- **Success Response:**

  **Code:** 200 <br />
  **Content:** `{ "response": {"username": "myemail@xx.com", "admin_approval": False}, "status": 200, "message": "Cliente salvo com sucesso!Aguarde o administrador do sistema te aprovar"}`

- **Error Response:**

  **Code:** 400 - Bad Request <br />
  **Content:** `{ "response": {}, "status": 400, "message": "A senha precisa conter entre 8 e 20 caracteres" }`

  OR

  **Code:** 400 - Bad Request <br />
  **Content:** `{ "response": {}, "status": 400, "message": "O cliente já existe na base de dados" }`

- **Sample Call:**

  ```javascript
  $.ajax({
    url: "/api/registrar-cliente",
    contentType: "application/json",
    dataType: "json",
    type: "POST",
    data: { email: "myemail@xx.com", password: "mypassword123" },
    success: function (r) {
      console.log(r);
    },
  });
  ```

  #### **Authentication**

  Send a post request to receive a token and make the other requests

  - **URL**

  /auth

- **Method:**

  `POST`

- **Data Params**

  {"username": "myemail@xx.com", "password": "this is my password"}

- **Success Response:**

  **Code:** 200 <br />
  **Content:** `{ ""access_token"": "xxYYzz918" }`

- **Error Response:**

  **Code:** 401 - Unauthorized <br />
  **Content:** `{ "description": "Invalid credentials", "error": "Bad Request", "status_code": 401}`

- **Sample Call:**

  ```javascript
  $.ajax({
    url: "/api",
    contentType: "application/json",
    dataType: "json",
    type: "POST",
    data: { username: "myemail@xx.com", password: "mypassword123" },
    success: function (r) {
      console.log(r);
    },
  });
  ```

  #### ** CID Recommendation**

  Send a post request to receive CID recomendation based on the patient case description

  - **URL**

  /api/recomendar-cid

- **Method:**

  `POST`

- **Data Params**

  {"case_desc": "patient case description"}

- **Success Response:**

  **Code:** 200 <br />
  **Content:** `{ "message": "Cid recomendado com sucesso", "response": {"code": "CID code", "desc": "Inseminação artificial", "id": cid_id, "relation": ""}, "status": 200}`

- **Error Response:**

  **Code:** 401 - Unauthorized <br />
  **Content:** `{ "description": "Not enough segments", "error": "Invalid token", "status_code": 401}`

- **Sample Call:**

  ```javascript
  $.ajax({
    url: "/api/recomendar-cid",
    headers: { Authorization: "JWT" + sessionStorage.getItem("token") },
    contentType: "application/json",
    dataType: "json",
    type: "POST",
    data: { username: "myemail@xx.com", password: "mypassword123" },
    success: function (r) {
      console.log(r);
    },
  });
  ```

  #### ** Customer Password Reset**

  Send a post request to receive an e-mail with password reset instructions

  - **URL**

  /api/reset-senha

- **Method:**

  `POST`

- **Data Params**

  {"username":"myemail@xx.com"}

- **Success Response:**

  **Code:** 200 <br />
  **Content:** `{ "message": "Um e-mail com as instruções para redefinir sua senha foi enviado :)", "response": {}, "status": 200}`

- **Error Response:**

  **Code:** 400 - Bad Request <br />
  **Content:** `{ "message": "Cliente não foi encontrado. Favor tentar outro e-mail :)", "response": {}, "status": 404}`

- **Sample Call:**

  ```javascript
  $.ajax({
    url: "/api/reset-senha",
    contentType: "application/json",
    dataType: "json",
    type: "POST",
    data: { username: "myemail@xx.com" },
    success: function (r) {
      console.log(r);
    },
  });
  ```

## License

[MIT](https://choosealicense.com/licenses/mit/)
