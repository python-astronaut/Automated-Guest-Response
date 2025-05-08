import os
import json
import re
import sys
from datetime import datetime
from string import Template

class GuestEmailGenerator:
    def __init__(self, templates_path="templates"):
        """Initialize the email generator with templates from the specified directory."""
        self.templates_path = templates_path
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load all template files from the templates directory."""
        # Create templates directory if it doesn't exist
        if not os.path.exists(self.templates_path):
            os.makedirs(self.templates_path)
            # Create default templates
            self._create_default_templates()
        
        # Load template files
        for filename in os.listdir(self.templates_path):
            if filename.endswith('.json'):
                template_type = filename.split('.')[0]
                with open(os.path.join(self.templates_path, filename), 'r') as file:
                    self.templates[template_type] = json.load(file)
    
    def _create_default_templates(self):
        """Create default templates if none exist."""
        default_templates = {
            "booking_confirmation": {
                "subject": "Booking Confirmation - $hotel_name",
                "body": """Dear $guest_name,

Thank you for choosing $hotel_name for your upcoming stay in $location. We are pleased to confirm your booking details:

Reservation Details:
- Check-in Date: $check_in_date
- Check-out Date: $check_out_date
- Room Type: $room_type
- Number of Guests: $num_guests
- Reservation Number: $reservation_number

We look forward to welcoming you on $check_in_date. Should you have any questions or special requests before your arrival, please don't hesitate to contact us.

Best regards,
$staff_name
$hotel_name
$hotel_contact
"""
            },
            "inquiry_response": {
                "subject": "Response to Your Inquiry - $hotel_name",
                "body": """Dear $guest_name,

Thank you for your interest in $hotel_name. We appreciate you reaching out to us regarding $inquiry_subject.

$custom_response

If you have any further questions, please feel free to contact us at $hotel_contact.

Best regards,
$staff_name
$hotel_name
"""
            },
            "special_request": {
                "subject": "Your Special Request - $hotel_name",
                "body": """Dear $guest_name,

Thank you for your special request regarding your upcoming stay at $hotel_name.

We have noted your request for $special_request and will do our best to accommodate it. $custom_response

If you have any additional requests or questions, please don't hesitate to let us know.

Best regards,
$staff_name
$hotel_name
$hotel_contact
"""
            },
            "checkout_reminder": {
                "subject": "Checkout Reminder - $hotel_name",
                "body": """Dear $guest_name,

We hope you've been enjoying your stay at $hotel_name.

This is a friendly reminder that your checkout is scheduled for tomorrow, $check_out_date, at $checkout_time. 

$late_checkout_policy

Please ensure all room keys are returned to the front desk upon departure. If you have any questions or need assistance with your luggage, our staff will be happy to help.

It has been our pleasure to host you, and we wish you safe travels.

Best regards,
$staff_name
$hotel_name
$hotel_contact
"""
            },
            "feedback_request": {
                "subject": "How was your stay? - $hotel_name",
                "body": """Dear $guest_name,

We hope you enjoyed your recent stay at $hotel_name from $check_in_date to $check_out_date.

Your feedback is extremely valuable to us, and we would appreciate if you could take a few minutes to share your experience. You can submit your review by $feedback_method.

Thank you for choosing $hotel_name. We look forward to welcoming you back in the future.

Best regards,
$staff_name
$hotel_name
$hotel_contact
"""
            }
        }
        
        # Save default templates to files
        for template_name, template_content in default_templates.items():
            with open(os.path.join(self.templates_path, f"{template_name}.json"), 'w') as file:
                json.dump(template_content, file, indent=4)
    
    def list_available_templates(self):
        """Return a list of available template types."""
        return list(self.templates.keys())
    
    def get_required_fields(self, template_type):
        """Extract required fields from a template."""
        if template_type not in self.templates:
            raise ValueError(f"Template type '{template_type}' not found.")
        
        # Use regex to find all variables in the format $variable_name
        template = self.templates[template_type]
        pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
        
        subject_fields = re.findall(pattern, template["subject"])
        body_fields = re.findall(pattern, template["body"])
        
        # Combine and remove duplicates
        all_fields = set(subject_fields + body_fields)
        return sorted(all_fields)
    
    def generate_email(self, template_type, guest_details):
        """Generate an email using the specified template and guest details."""
        if template_type not in self.templates:
            raise ValueError(f"Template type '{template_type}' not found.")
        
        # Get template
        template = self.templates[template_type]
        
        # Check for missing required fields
        required_fields = self.get_required_fields(template_type)
        missing_fields = [field for field in required_fields if field not in guest_details]
        
        if missing_fields:
            raise ValueError(f"Missing required guest details: {', '.join(missing_fields)}")
        
        # Fill in templates
        subject_template = Template(template["subject"])
        body_template = Template(template["body"])
        
        subject = subject_template.substitute(guest_details)
        body = body_template.substitute(guest_details)
        
        return {
            "to": guest_details.get("guest_email", ""),
            "subject": subject,
            "body": body
        }
    
    def add_template(self, template_name, subject_template, body_template):
        """Add a new email template."""
        if template_name in self.templates:
            raise ValueError(f"Template '{template_name}' already exists.")
        
        # Create and save the new template
        template = {
            "subject": subject_template,
            "body": body_template
        }
        
        self.templates[template_name] = template
        
        # Save to file
        with open(os.path.join(self.templates_path, f"{template_name}.json"), 'w') as file:
            json.dump(template, file, indent=4)
        
        return template_name
    
    def update_template(self, template_name, subject_template=None, body_template=None):
        """Update an existing email template."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found.")
        
        template = self.templates[template_name]
        
        if subject_template is not None:
            template["subject"] = subject_template
        
        if body_template is not None:
            template["body"] = body_template
        
        # Save changes to file
        with open(os.path.join(self.templates_path, f"{template_name}.json"), 'w') as file:
            json.dump(template, file, indent=4)
        
        return template_name
    
    def delete_template(self, template_name):
        """Delete an email template."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found.")
        
        # Remove from dict
        del self.templates[template_name]
        
        # Remove file
        template_path = os.path.join(self.templates_path, f"{template_name}.json")
        if os.path.exists(template_path):
            os.remove(template_path)
        
        return template_name


def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_menu():
    """Print the main menu options."""
    print("\n===== Guest Email Response Generator =====")
    print("1. Generate an email")
    print("2. View available templates")
    print("3. Create a new template")
    print("4. Update an existing template")
    print("5. Delete a template")
    print("6. Exit")
    print("=========================================")


def get_template_selection(generator):
    """Get template selection from user."""
    templates = generator.list_available_templates()
    print("\nAvailable templates:")
    for i, template in enumerate(templates, 1):
        print(f"{i}. {template}")
    
    while True:
        try:
            choice = int(input("\nSelect a template (number): "))
            if 1 <= choice <= len(templates):
                return templates[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")


def collect_guest_details(generator, template_type):
    """Collect guest details for the selected template."""
    required_fields = generator.get_required_fields(template_type)
    guest_details = {}
    
    print(f"\nPlease provide the following information for the {template_type} email:")
    for field in required_fields:
        # Format the field name for better readability
        field_display = field.replace('_', ' ').title()
        value = input(f"{field_display}: ")
        guest_details[field] = value
    
    return guest_details


def generate_email_flow(generator):
    """Flow for generating an email."""
    template_type = get_template_selection(generator)
    guest_details = collect_guest_details(generator, template_type)
    
    try:
        email = generator.generate_email(template_type, guest_details)
        
        clear_screen()
        print("\n===== Generated Email =====")
        print(f"To: {email['to']}")
        print(f"Subject: {email['subject']}")
        print(f"\nBody:\n{email['body']}")
        print("==========================")
        
        # Option to save to file
        save_option = input("\nWould you like to save this email to a file? (y/n): ")
        if save_option.lower() == 'y':
            filename = input("Enter filename (default: email.txt): ") or "email.txt"
            with open(filename, 'w') as file:
                file.write(f"To: {email['to']}\n")
                file.write(f"Subject: {email['subject']}\n\n")
                file.write(f"{email['body']}")
            print(f"Email saved to {filename}")
    
    except ValueError as e:
        print(f"Error: {e}")
        input("Press Enter to continue...")


def view_templates(generator):
    """View available templates and their details."""
    templates = generator.list_available_templates()
    
    if not templates:
        print("No templates available.")
        return
    
    print("\nAvailable templates:")
    for i, template_name in enumerate(templates, 1):
        print(f"{i}. {template_name}")
    
    while True:
        try:
            choice = input("\nEnter a number to view template details (or 'b' to go back): ")
            if choice.lower() == 'b':
                return
            
            choice = int(choice)
            if 1 <= choice <= len(templates):
                template_name = templates[choice - 1]
                template = generator.templates[template_name]
                
                clear_screen()
                print(f"\n===== Template: {template_name} =====")
                print("Subject:", template['subject'])
                print("\nBody:")
                print(template['body'])
                print("\nRequired fields:", ", ".join(generator.get_required_fields(template_name)))
                print("===============================")
                
                input("\nPress Enter to continue...")
                return view_templates(generator)
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number or 'b'.")


def create_template(generator):
    """Create a new email template."""
    template_name = input("\nEnter a name for the new template (lowercase, no spaces): ")
    
    # Validate template name
    if not re.match(r'^[a-z_][a-z0-9_]*$', template_name):
        print("Invalid template name. Use lowercase letters, numbers, and underscores only.")
        input("Press Enter to continue...")
        return
    
    if template_name in generator.templates:
        print(f"Template '{template_name}' already exists.")
        input("Press Enter to continue...")
        return
    
    print("\nEnter the subject template (use $variable_name for variables):")
    subject = input("> ")
    
    print("\nEnter the body template (use $variable_name for variables):")
    print("Type '.' on a new line when finished:")
    
    lines = []
    while True:
        line = input()
        if line == '.':
            break
        lines.append(line)
    
    body = "\n".join(lines)
    
    try:
        generator.add_template(template_name, subject, body)
        print(f"\nTemplate '{template_name}' created successfully.")
        print("Required fields:", ", ".join(generator.get_required_fields(template_name)))
    except ValueError as e:
        print(f"Error: {e}")
    
    input("Press Enter to continue...")


def update_template(generator):
    """Update an existing email template."""
    template_name = get_template_selection(generator)
    template = generator.templates[template_name]
    
    print(f"\nCurrent subject: {template['subject']}")
    print("Enter new subject (or press Enter to keep current):")
    subject = input("> ")
    subject = subject if subject else None
    
    print(f"\nCurrent body:")
    print(template['body'])
    print("\nEnter new body (or press Enter to keep current):")
    print("If updating, type '.' on a new line when finished:")
    
    if input("Update body? (y/n): ").lower() == 'y':
        lines = []
        while True:
            line = input()
            if line == '.':
                break
            lines.append(line)
        body = "\n".join(lines)
    else:
        body = None
    
    try:
        generator.update_template(template_name, subject, body)
        print(f"\nTemplate '{template_name}' updated successfully.")
    except ValueError as e:
        print(f"Error: {e}")
    
    input("Press Enter to continue...")


def delete_template(generator):
    """Delete an email template."""
    template_name = get_template_selection(generator)
    
    confirm = input(f"\nAre you sure you want to delete the template '{template_name}'? (y/n): ")
    if confirm.lower() == 'y':
        try:
            generator.delete_template(template_name)
            print(f"Template '{template_name}' deleted successfully.")
        except ValueError as e:
            print(f"Error: {e}")
    else:
        print("Deletion cancelled.")
    
    input("Press Enter to continue...")


def main():
    """Main function to run the interactive email generator."""
    generator = GuestEmailGenerator()
    
    while True:
        clear_screen()
        print_menu()
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            generate_email_flow(generator)
        elif choice == '2':
            view_templates(generator)
        elif choice == '3':
            create_template(generator)
        elif choice == '4':
            update_template(generator)
        elif choice == '5':
            delete_template(generator)
        elif choice == '6':
            print("\nThank you for using the Guest Email Response Generator. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
