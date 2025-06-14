# Use a base image with pre-installed scientific Python packages for faster builds
FROM jupyter/scipy-notebook:python-3.10

# The base image runs as jovyan user. Switch to root to copy files and set permissions.
USER root

# Set working directory
WORKDIR /home/jovyan/work

# Copy requirements file and application code, and set ownership to the jovyan user
COPY --chown=jovyan:users . .

# Switch back to the jovyan user for subsequent commands
USER jovyan

# Install the remaining application-specific dependencies
# This will be much faster as most libraries are in the base image
RUN pip install uv && uv pip install --system --no-cache-dir -r requirements.txt


# Expose the port the app runs on
EXPOSE 8050

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server"]
