import React, { useState } from "react";
import { Form, Container, Row, Col, Button } from "react-bootstrap";
import "./Compiler.css";

const Compiler = () => {
	const [input, setInput] = useState("");
	const [result, setResult] = useState("");
	// const [userInput, setUserInput] = useState("");

	const submit = (event) => {
		event.preventDefault();
		let url = "http://127.0.0.1:5000/compile";
		// let resetUrl = "http://127.0.0.1:5000/compile-reset";
		let API_TOKEN = "ELDA";
		let data = {
			codigo: input,
		};
		console.log(data);
		let settings = {
			method: "POST",
			headers: {
				Authorization: `Bearer ${API_TOKEN}`,
				"Content-Type": "application/json",
			},
			body: JSON.stringify(data),
		};
		fetch(url, settings)
			.then((response) => {
				console.log(response);
				if (response.ok) {
					return response.json();
				}
				throw new Error(response.statusText);
			})
			.then((responseJSON) => {
				console.log(responseJSON);
				let tempOutput = "";
				for (let key in responseJSON) {
					if (responseJSON.hasOwnProperty(key)) {
						console.log(key + " -> " + responseJSON[key]);
						tempOutput += `${key} -> ${responseJSON[key]}\n`;
					}
				}
				setResult(tempOutput);
				return responseJSON;
			})
			.catch((err) => {
				console.log(err);
			});
	};
	return (
		<Container id='formContainer'>
			<Form id='formEmpresa' noValidate onSubmit={submit}>
				<Row xs={6} sm={6} md={6} lg={6} xl={6}>
					<Col xs={6} sm={6} md={6} lg={6} xl={6}>
						<Form.Group controlId=''>
							<Form.Label>Code</Form.Label>
							<Form.Control
								as='textarea'
								rows={30}
								value={input}
								onChange={(e) => setInput(e.target.value)}
							/>
						</Form.Group>
					</Col>
					<Col xs={6} sm={6} md={6} lg={6} xl={6}>
						<Form.Group controlId=''>
							<Form.Label>Output</Form.Label>
							<Form.Control
								as='textarea'
								rows={30}
								value={result}
								onChange={(e) => setResult(e.target.value)}
							/>
						</Form.Group>
					</Col>
				</Row>
				<Row>
					<Form.Group>
						<Button type='submit'>Compile</Button>
					</Form.Group>
				</Row>
				<Row>
					<Col>
						<Form.Group controlId=''>
							<Form.Label>User Input</Form.Label>
							<Form.Control as='textarea' rows={10} />
						</Form.Group>
					</Col>
				</Row>
			</Form>
		</Container>
	);
};

export default Compiler;
