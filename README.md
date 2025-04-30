# Child Stunting Monitoring System

A comprehensive Django-based web application for monitoring, analyzing, and addressing child stunting through data-driven insights and AI assistance.

![Python](https://img.shields.io/badge/Python-69.4%25-blue.svg)
![HTML](https://img.shields.io/badge/HTML-26.1%25-orange.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-4.5%25-yellow.svg)


---

## 📋 Overview

The **Child Stunting Monitoring System** provides healthcare professionals, parents, and researchers with tools to:
- Track child growth.
- Identify stunting risks.
- Access evidence-based interventions.

The system integrates:
- **Measurement tracking**.
- **AI-powered analysis**.
- **Educational resources**.
- **Visualization dashboards**.

---

## ✨ Features

- **User Role Management**: Different access levels for healthcare providers, parents, and researchers.
- **Growth Measurement Tracking**: Record and monitor children's growth parameters.
- **AI-Powered Analysis**: Intelligent assessment of growth patterns and risk factors.
- **Interactive Dashboards**: Visualize growth data and population trends.
- **Educational Resources**: Articles and guides on child nutrition and development.
- **REST API**: Programmatic access to system data.

---

## 🔧 Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/gabrieljumanne/Stunting_AI_system.git
   cd Stunting_AI_system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Web interface: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - Admin panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🏗️ Project Structure

```plaintext
Stunting_AI_system/
├── core/               # User authentication and role management
├── measurement/        # Growth measurement recording and analysis
├── ai_assistance/      # AI-powered insights and recommendations
├── dashboard/          # Data visualization tools
├── articles/           # Educational content management
├── static/             # Static assets (CSS, JavaScript, images)
├── templates/          # HTML templates
├── manage.py           # Django management script
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your_secret_key
DEBUG=True
OPEN_ROUTER_KEY=your_open_router_api_key
```

---

## 📊 Usage

### User Roles

1. **Healthcare Providers**: 
   - Record and track children's measurements.
   - Access AI-powered growth assessments.
   - View comprehensive dashboards.

2. **Parents**: 
   - Monitor their children's growth progress.
   - Access educational resources.
   - Receive personalized recommendations.

3. **Researchers**:
   - Analyze population-level data.
   - Generate reports and insights.

### Main Workflows

1. **Growth Monitoring**
   - Record measurements (height, weight, etc.).
   - Track growth over time.
   - Compare to standard growth charts.

2. **Intervention Planning**
   - Identify stunting risks early.
   - Access evidence-based interventions.
   - Monitor intervention effectiveness.

3. **Resource Access**
   - Browse educational articles.
   - Receive personalized content recommendations.
   - Access nutrition and development guidelines.

---

## 🔐 Security Notes

- The project uses Django's security middleware.
- Role-based access controls are implemented.
- API endpoints are secured with authentication.

---



---

## 👥 Contributing

Contributions are welcome! If you would like to contribute to this project, please follow the steps below:

1. Fork the repository.
2. Create a branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature or fix description"
   ```
4. Push the branch to your forked repository:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request to this repository.

---

## 👤 Author

This project was created by **Gabriel Wambura (Gabriel Jumanne)**. For inquiries or feedback, feel free to reach out via [GitHub](https://github.com/gabrieljumanne).

---

Feel free to explore, contribute, and make a difference!
