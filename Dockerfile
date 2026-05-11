FROM odoo:18

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /mnt/extra-addons && chown -R odoo:odoo /mnt/extra-addons

COPY ./odoo_prod.conf /etc/odoo/odoo.conf
RUN chown odoo:odoo /etc/odoo/odoo.conf

COPY ./odoo/addons /mnt/extra-addons
RUN chown -R odoo:odoo /mnt/extra-addons

# Create a bulletproof entrypoint that ignores ANY cached Railway commands
# and correctly maps Railway's database variables to Odoo's expectations.
RUN echo '#!/bin/bash' > /run_odoo.sh && \
    echo 'export HOST=$PGHOST' >> /run_odoo.sh && \
    echo 'export PORT=$PGPORT' >> /run_odoo.sh && \
    echo 'export USER=$PGUSER' >> /run_odoo.sh && \
    echo 'export PASSWORD=$PGPASSWORD' >> /run_odoo.sh && \
    echo 'echo "Starting Odoo with clean environment..."' >> /run_odoo.sh && \
    echo 'exec /entrypoint.sh odoo -d "$PGDATABASE"' >> /run_odoo.sh && \
    chmod +x /run_odoo.sh

USER odoo

# Use our custom script as the absolute entrypoint.
# This prevents Railway's buggy startCommand from passing $PGPORT as an argument.
ENTRYPOINT ["/run_odoo.sh"]