from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flasgger import Swagger
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Swagger configuration
    swagger_config = Swagger.DEFAULT_CONFIG.copy()
    swagger_config.update({
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    })

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Airplane Food Trolley Management API",
            "description": "REST API for tracking airplane food trolley inventory with batch-level tracking, drawer management, and employee performance evaluation. **Critical Feature**: Batch Stacking Prevention - Returns HTTP 207 when loading batches over non-depleted batches.",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": ["http", "https"],
        "tags": [
            {"name": "Health", "description": "Health check endpoints"},
            {"name": "Items", "description": "Item batch operations"},
            {"name": "Drawers", "description": "Drawer operations"},
            {"name": "Drawer Layouts", "description": "Drawer layout operations"},
            {"name": "Drawer Status", "description": "Drawer status operations (CRITICAL: Batch stacking detection)"},
            {"name": "Employees", "description": "Employee operations"},
            {"name": "Restock History", "description": "Restock history and performance evaluation"}
        ]
    }

    # Initialize Swagger
    app.config['SWAGGER'] = swagger_config
    Swagger(app, template=swagger_template)

    # Import models (needed for migrations)
    with app.app_context():
        from app import models

    # Register blueprints
    from app.routes import items, drawers, drawer_layouts, drawer_status, employees, restock_history
    app.register_blueprint(items.bp)
    app.register_blueprint(drawers.bp)
    app.register_blueprint(drawer_layouts.bp)
    app.register_blueprint(drawer_status.bp)
    app.register_blueprint(employees.bp)
    app.register_blueprint(restock_history.bp)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        """
        Health check endpoint
        ---
        tags:
          - Health
        responses:
          200:
            description: Service is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
                service:
                  type: string
                  example: airplane-trolley-api
        """
        return jsonify({'status': 'healthy', 'service': 'airplane-trolley-api'}), 200

    # API Routes listing endpoint
    @app.route('/api', methods=['GET'])
    @app.route('/api/', methods=['GET'])
    def api_routes():
        """
        List all API endpoints
        ---
        tags:
          - Health
        responses:
          200:
            description: List of all available API endpoints
        """
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static' and '/flasgger' not in str(rule):
                routes.append({
                    'endpoint': str(rule),
                    'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'}))
                })

        # Group routes by resource
        resources = {
            'health': [],
            'items': [],
            'drawers': [],
            'drawer_layouts': [],
            'drawer_status': [],
            'employees': [],
            'restock_history': []
        }

        for route in sorted(routes, key=lambda x: x['endpoint']):
            endpoint = route['endpoint']
            if '/api/items' in endpoint:
                resources['items'].append(route)
            elif '/api/drawers' in endpoint and 'layout' not in endpoint:
                resources['drawers'].append(route)
            elif '/api/drawer-layout' in endpoint:
                resources['drawer_layouts'].append(route)
            elif '/api/drawer-status' in endpoint:
                resources['drawer_status'].append(route)
            elif '/api/employees' in endpoint:
                resources['employees'].append(route)
            elif '/api/restock-history' in endpoint:
                resources['restock_history'].append(route)
            elif '/health' in endpoint or endpoint == '/api' or endpoint == '/api/':
                resources['health'].append(route)

        return jsonify({
            'service': 'Airplane Food Trolley Management API',
            'version': '1.0.0',
            'documentation': '/docs',
            'total_endpoints': len(routes),
            'resources': resources
        }), 200

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': {'code': 'NOT_FOUND', 'message': 'Resource not found'}}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'}}), 500

    return app
