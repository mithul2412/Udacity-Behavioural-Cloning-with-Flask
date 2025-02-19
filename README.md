# Udacity Behavioural Cloning with Flask

## Description
This project implements behavioural cloning for autonomous driving in the Udacity Self-Driving Car Simulator. It combines deep learning for imitating human driving behavior with a Flask web application that demonstrates real-time model inference. The system processes input from images or video streams and outputs steering commands, allowing you to visualize and interact with the model's predictions. The project was done as a part of Neural Networks Course taken in my bachelors.

## Key Features
- Behavioural Cloning Model: Utilizes deep neural networks (built with TensorFlow/Keras) to learn driving behaviors from recorded data.
- Flask Web Interface: Offers an interactive environment to test the trained model in real time.
- Real-Time Inference: Processes live video feeds or pre-recorded images to generate steering commands.
- Visualization and Logging: Displays model predictions and performance metrics on the web dashboard.
- Adversarial Attack and Defense Exploration: Investigated adversarial attacks and defenses using CleverHans to evaluate the robustness of the cloning model against malicious perturbations. This exploration aids in understanding vulnerabilities and implementing effective countermeasures to enhance model security.

## Technologies Used
- **Python** for all core functionalities.
- **TensorFlow/Keras** to build and train the behavioural cloning model.
- **Flask** to create the web application interface.
- **OpenCV** for image processing and handling video streams.
- **CleverHans** for implementing adversarial attack and defense techniques.
- **Jupyter Notebooks** (optional) for experiments and evaluation.
