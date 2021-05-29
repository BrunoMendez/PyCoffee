// https://pycoffeecompiler.herokuapp.com/
import React, { useState, useRef, useEffect } from "react";
import { Form, Container, Row, Col, Button } from "react-bootstrap";
import "./Compiler.css";
/* import fetchAPI from '../helpers/request'; */
let base_url = "https://pycoffeecompiler.herokuapp.com/";
let API_TOKEN = "ELDA";
const Compiler = () => {
	const [input, setInput] = useState("");
	const [result, setResult] = useState("");
	const userInputRef = useRef();
	const formRef = useRef();
	const [isWaitingForInput, setIsWaitingForInput] = useState(false);
	const [height, setHeight] = useState();
	const [inputLabel, setInputLabel] = useState("");
	const [currentQuad, setCurrentQuad] = useState(0);

	const fetchUrl = (url, settings) => {
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
						if (Array.isArray(responseJSON[key])) {
							if ((responseJSON[key][0] = "INPUT_REQUEST")) {
								setCurrentQuad(responseJSON[key][1]);
								setIsWaitingForInput(true);
								userInputRef.current.focus();
								setInputLabel(
									"Ingrese un valor y presione respond"
								);
							}
						} else {
							tempOutput += `${responseJSON[key]}\n`;
						}
					}
				}
				setResult((prevState) => prevState + tempOutput);
				return responseJSON;
			})
			.catch((err) => {
				console.log(err);
			});
	};
	const submit = (event) => {
		event.preventDefault();
		let url = base_url + "compile";
		console.log(url);
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
		fetchUrl(url, settings);
		setResult("");
	};

	const sendInput = (event) => {
		event.preventDefault();
		setInputLabel("");
		setIsWaitingForInput(false);
		let url = base_url + "user-input";
		console.log(userInputRef.current.value);
		let data = {
			input_value: userInputRef.current.value,
			current_quad: currentQuad,
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
		fetchUrl(url, settings);
		userInputRef.current.value = "";
	};
	useEffect(() => {
		function handleResize() {
			setHeight(window.innerHeight);
		}

		window.addEventListener("resize", handleResize);
	});

	return (
		<Container id='formContainer'>
			<Form id='formEmpresa' noValidate onSubmit={submit}>
				<Row xs={6} sm={6} md={6} lg={6} xl={6}>
					<Col xs={6} sm={6} md={6} lg={6} xl={6}>
						<Form.Group controlId=''>
							<Form.Label>Code</Form.Label>
							<Form.Control
								as='textarea'
								style={{
									height: "80%",
									lineHeight: 1,
									fontSize: "12px",
								}}
								rows={parseInt((height / 12) * 0.5)}
								value={input}
								onChange={(e) => setInput(e.target.value)}
								disabled={isWaitingForInput}
							/>
						</Form.Group>
					</Col>
					<Col xs={6} sm={6} md={6} lg={6} xl={6}>
						<Form.Group controlId=''>
							<Form.Label>Output</Form.Label>
							<Form.Control
								as='textarea'
								style={{
									height: "80%",
									lineHeight: 1,
									fontSize: "12px",
								}}
								rows={parseInt((height / 12) * 0.5)}
								value={result}
								readOnly
							/>
						</Form.Group>
					</Col>
				</Row>
				<Row>
					<Form.Group>
						<Button type='submit' disabled={isWaitingForInput}>
							Compile
						</Button>
					</Form.Group>
				</Row>
			</Form>
			<Form
				id='formEmpresa'
				noValidate
				onSubmit={sendInput}
				ref={formRef}
			>
				<Row>
					<Col>
						<Form.Label>{inputLabel}</Form.Label>
						<Form.Group controlId=''>
							<Form.Label>User Input</Form.Label>
							<Form.Control
								as='textarea'
								rows={1}
								ref={userInputRef}
								disabled={!isWaitingForInput}
								onKeyPress={(e) => {
									if (e.charCode === 13) {
										sendInput(e);
									}
								}}
							/>
						</Form.Group>
					</Col>
				</Row>
				<Row>
					<Form.Group>
						<Button type='submit' disabled={!isWaitingForInput}>
							Respond
						</Button>
					</Form.Group>
				</Row>
			</Form>
		</Container>
	);
};

export default Compiler;
