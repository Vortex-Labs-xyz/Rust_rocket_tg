#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}╭──────────────────────────────────────────────────────────────╮${NC}"
    echo -e "${PURPLE}│${NC} ${CYAN}🔒 Secure Environment Setup${NC}                               ${PURPLE}│${NC}"
    echo -e "${PURPLE}╰──────────────────────────────────────────────────────────────╯${NC}"
    echo
}

setup_gitignore() {
    print_status "Setting up .gitignore..."
    
    if [ -f ".gitignore" ]; then
        print_warning ".gitignore already exists, checking entries..."
        
        entries=(".env" ".env.example" "*.session" ".venv/")
        for entry in "${entries[@]}"; do
            if ! grep -q "^${entry}$" .gitignore; then
                echo "$entry" >> .gitignore
                print_success "Added $entry to .gitignore"
            else
                print_status "$entry already in .gitignore"
            fi
        done
    else
        cat > .gitignore << 'EOF'
.env
.env.example
*.session
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.DS_Store
*.log
EOF
        print_success ".gitignore created successfully"
    fi
}

setup_env_example() {
    print_status "Setting up .env.example..."
    
    cat > .env.example << 'EOF'
API_ID=
API_HASH=
PHONE=
CHANNEL=
EOF
    
    print_success ".env.example created successfully"
}

setup_env() {
    print_status "Setting up .env..."
    
    if [ -f ".env" ]; then
        print_warning ".env already exists, skipping creation"
        return
    fi
    
    cat > .env << 'EOF'
API_ID=  # TODO: eintragen
API_HASH=  # TODO: eintragen
PHONE=  # TODO: eintragen
CHANNEL=  # TODO: eintragen
EOF
    
    print_success ".env created with TODO markers"
    print_warning "Remember to fill in your actual values in .env!"
}

set_permissions() {
    print_status "Setting secure permissions..."
    
    if [ -f ".env" ]; then
        chmod 600 .env
        print_success "Set .env permissions to 600 (owner read/write only)"
    fi
    
    if [ -f ".env.example" ]; then
        chmod 644 .env.example
        print_success "Set .env.example permissions to 644"
    fi
}

main() {
    print_header
    
    setup_gitignore
    echo
    
    setup_env_example
    echo
    
    setup_env
    echo
    
    set_permissions
    echo
    
    print_success "Environment setup completed!"
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. ${CYAN}Edit .env${NC} and replace TODO comments with actual values"
    echo -e "  2. ${CYAN}pip install -r requirements.txt${NC} to install dependencies"
    echo -e "  3. ${CYAN}python boost_manager.py${NC} to start using the bot"
    echo
}

main "$@" 