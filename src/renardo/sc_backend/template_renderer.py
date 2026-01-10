"""
SuperCollider template renderer using Jinja2.
Loads .sc.j2 templates and renders them with variables from settings.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from renardo.settings_manager import settings


class SCTemplateRenderer:
    """Renders SuperCollider class templates using Jinja2."""

    def __init__(self):
        """Initialize Jinja2 environment with templates directory."""
        self.templates_dir = Path(__file__).parent / 'templates'

        # Ensure templates directory exists
        if not self.templates_dir.exists():
            raise FileNotFoundError(
                f"SC templates directory not found: {self.templates_dir}"
            )

        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),  # No autoescape for .sc files
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

    def _get_template_variables(self):
        """
        Extract template variables from settings.

        Returns:
            dict: Variables to pass to Jinja2 templates
        """
        return {
            'osc_port': settings.get("sc_backend.PORT"),
            'num_output_channels': settings.get("sc_backend.NUM_OUTPUT_BUS_CHANNELS"),
            'num_input_channels': settings.get("sc_backend.NUM_INPUT_BUS_CHANNELS"),
        }

    def render_template(self, template_name: str, **extra_vars) -> str:
        """
        Render a template with variables from settings.

        Args:
            template_name (str): Name of template file (e.g., 'Renardo.sc.j2')
            **extra_vars: Additional variables to pass to template

        Returns:
            str: Rendered template content

        Raises:
            jinja2.TemplateNotFound: If template file doesn't exist
        """
        template = self.env.get_template(template_name)
        variables = self._get_template_variables()
        variables.update(extra_vars)
        return template.render(**variables)

    def render_renardo_class(self) -> str:
        """
        Render the Renardo.sc class template.

        Returns:
            str: Rendered Renardo.sc content
        """
        return self.render_template('Renardo.sc.j2')

    def render_stagelimiter_class(self) -> str:
        """
        Render the StageLimiter.sc class template.

        Returns:
            str: Rendered StageLimiter.sc content
        """
        return self.render_template('StageLimiter.sc.j2')
