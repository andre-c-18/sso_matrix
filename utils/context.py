"""
Context processors and template fixes
"""
import os


def register_context_processors(app):
    @app.context_processor
    def inject_globals():
        import flask
        return {
            'sso_base': os.getenv('SSO_BASE_URL', 'http://localhost:5000'),
            'session': flask.session,
        }
