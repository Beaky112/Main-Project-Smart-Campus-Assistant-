from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import random
import datetime
import re
import logging
from urllib.parse import quote
from typing import Optional

logger = logging.getLogger(__name__)

class Chatbot:
    """
    College enquiry chatbot with multi-feature support.
    """

    MAX_INPUT_LENGTH = 200
    SIMILARITY_THRESHOLD = 0.7

    COURSE_DATA = {
        'cse': {
            'name': 'Computer Science Engineering',
            'duration': '4 years',
            'fees': '1,50,000/year',
            'specializations': ['AI', 'Cloud Computing', 'IoT'],
            'website': '/cse'
        },
        'ece': {
            'name': 'Electronics and Communication Engineering',
            'duration': '4 years',
            'fees': '1,50,000/year',
            'specializations': ['VLSI', 'Embedded Systems'],
            'website': '/ece'
        },
        'eee': {
            'name': 'Electrical and Electronics Engineering',
            'duration': '4 years',
            'fees': '1,50,000/year',
            'specializations': ['Power Systems', 'Control Systems'],
            'website': '/eee'
        },
        'civil': {
            'name': 'Civil Engineering',
            'duration': '4 years',
            'fees': '1,50,000/year',
            'specializations': ['Structural Engineering', 'Environmental Engineering'],
            'website': '/civil'
        },
        'mech': {
            'name': 'Mechanical Engineering',
            'duration': '4 years',
            'fees': '1,50,000/year',
            'specializations': ['Thermal Engineering', 'Manufacturing'],
            'website': '/mech'
        },
        'mining': {
            'name': 'Mining Engineering',
            'duration': '4 years',
            'fees': '1,50,000/year',
            'specializations': ['Mine Planning', 'Mineral Processing'],
            'website': '/mining'
        },
        'aiml': {
            'name': 'Artificial Intelligence and Machine Learning',
            'duration': '4 years',
            'fees': '1,50,000/year',
            'specializations': ['Deep Learning', 'Computer Vision'],
            'website': '/aiml'
        }
    }

    transport_locations = {
        "kolar": "Yes, you will get transport facilities from Kolar to the campus. For more details contact R N Chandra Kumar Gowda",
        "bangarpet": "Yes, transport facilities are available from Bangarapet. For more details contact R N Chandra Kumar Gowda",
        "mulbagal": "Yes, transport facilities are available from Mulbagal. For more details contact R N Chandra Kumar Gowda",
        "kgf": "Yes, transport facilities are available from KGF. For more details contact R N Chandra Kumar Gowda",
    }

    RESPONSE_TEMPLATES = {
        "greetings": {
            "hello": "Hello! Welcome to {college_name}. How can I assist you today?",
            "hi": "Hi there! How can I help you with {college_name} information?",
            "good morning": "Good morning! Welcome to {college_name}. How may I help you today?",
            "good afternoon": "Good afternoon! Welcome to {college_name}. How may I assist you?",
            "good evening": "Good evening! Welcome to {college_name}. How can I help you?",
            "how many courses are there?": "The college offers Computer Science Engineering, Electronics and Communication Engineering, Electrical and Electronics Engineering, Civil Engineering, Mining Engineering, Mechanical Engineering and Artificial Intelligence and Machine Learning",
            "what all facilities does the college offer": "The college offers a variety of facilities including:\n- High-speed WiFi\n- Well-equipped gym\n- Library with digital resources\n- Sports facilities\n- Transport services\n- Hostel accommodation",
            "does the college provide transport facilities": "Yes, the college provides transport facilities for students residing in Kolar district and nearby areas.",
            "courses offered": "We offer the following courses:\n- Computer Science Engineering\n- Electronics and Communication Engineering\n- Electrical and Electronics Engineering\n- Civil Engineering\n- Mechanical Engineering\n- Mining Engineering\n- Artificial Intelligence and Machine Learning",
            "facilities provided at hostel?":"The facilities offered at college hostel are:\n Dining Facility with unlimited Food.\n Medical Facility.\n 24-hours Cold and hot water availability.\n Wi-Fi Enabled Campus.\n 24-hour CCTV Security.\n 24-hours RO drinking water facility.\n Library Facility (at Girls Hostel apart from Central Facility)\n Gym at Girls Hostel & for Boys at Block C Hostel\n Recreational Facility\n For more details contact Mr. Chandra Kumar Gowda R N",
            "for admission who should i contact":"you can contact Mr. Thangaraj. R",
            "food menu in canteen?":"Morning: IDLY\n Vada\n DOSA\n CHITRANA \n BISIBELEBATH \n PULIYOGRE\n Afternoon: MEALS\n RICEBATH \n You get everything at the cost for just 40 Rs.",
            "where can i find account section?":"you can find account section at president block lobby",
            "where is computer lab?":"the computer lab is at third floor of academic block ",
        },
        "college_info": {
            "principal": "Our Principal is {principal_name} ({principal_email})",
            "vice principal": "Our Vice Principal is {vice_principal_name} ({vice_principal_email})",
            "dean": "Our Dean is {dean_name} ({dean_email})",
            "admission": (
                "📋 Admission Process:\n"
                "1. Online Application\n"
                "2. Entrance Exam\n"
                "3. Personal Interview\n"
                "4. Document Verification\n\n"
                "For more details, visit our website or contact the admission office."
            ),
            "contact": (
                "📞 Contact Us:\n"
                "Phone: {phone}\n"
                "Email: {email}\n"
                "Address: {address}\n\n"
                "Office hours: 9:00 AM to 4:00 PM (Monday to Friday)"
            ),
            "about": (
                "🏫 About {college_name}:\n"
                "Established in 1986 by Dr. T. Thimmaiah, Ph.D (London), IAS (Retired), as the founder President.\n"
                "We offer quality education in engineering and technology fields with the sole purpose of imparting quality technical education.\n"
                "Our campus spans over 25 acres with state-of-the-art infrastructure."
            ),
            "facilities": (
                "🏆 College Facilities:\n"
                "- Modern classrooms with smart boards\n"
                "- Well-equipped laboratories\n"
                "- Central library with digital resources\n"
                "- Sports complex\n"
                "- Hostel facilities\n"
                "- Cafeteria\n"
                "- Medical center\n"
                "- Transport services"
            )
        }
    }

    PROFESSORS = {
        "kareemulla": {
            "name": "Dr. Mohamed Kareemulla",
            "department": "Computer Science",
            "qualification": "PhD",
            "experience": "28 years",
            "email": "kareemulla@drttit.edu.in",
            "research": "AI and ML",
            "position": "Professor"
        },
        "kharmega": {
            "name": "Dr. G. Kharmega Sundararaj",
            "department": "Computer Science",
            "qualification": "PB.E.,M.E.,PhD.",
            "experience": "24 years",
            "email": "drkharmegam@drttit.edu.in",
            "research": "Software Engineering",
            "position": "Associate Professor"
        },
        "jansi": {
            "name": "Dr. Jansi Rani J",
            "department": "Computer Science",
            "qualification": "MTech, Ph.D",
            "experience": "17 years",
            "email": "jansirani@drttit.edu.in",
            "Specialization": "Computer Science and engineering",
            "position": "Assistant Professor"
        },
        "   Preethi": {
            "name": "Ms. Preethi S",
            "department": "Computer Science",
            "qualification": "MTech, Ph.D",
            "experience": "8 years",
            "email": "preethi@drttit.edu.in",
            "Specialization": "Computer Science and engineering",
            "position": "Assistant Professor"
        },
        "velantina": {
            "name": "Ms. Velantina V",
            "department": "Computer Science",
            "qualification": "MTech",
            "experience": "2.1 years",
            "email": "velantina@drttit.edu.in",
            "Specialization": "Computer Science and engineering",
            "position": "Assistant Professor"
        },
        "thara devi": {
            "name": "Ms. Thara devi M",
            "department": "Computer Science",
            "qualification": "MTech",
            "experience": "16 years",
            "email": "thara@drttit.edu.in",
            "Specialization": "Computer Science and engineering",
            "position": "Assistant Professor"
        },
        "shalini": {
            "name": "Ms. Shalini G",
            "department": "Computer Science",
            "qualification": "MTech",
            "experience": "12.3 years",
            "email": "shalini@drttit.edu.in",
            "Specialization": "Computer Science and engineering",
            "position": "Assistant Professor"
        },
    }

    HODS = {
        "cse": {
            "name": "Dr. Geetha C. Megharaj",
            "department": "Computer Science",
            "qualification": "MS, M.TECH, PhD",
            "experience": "27 years",
            "email": "hodcse@drttit.edu.in",
            "specialization": "Computer Science Engineering",
            "research": "Computer Science"
        },
        "ece": {
            "name": "Dr. Vijaya Bharthi M",
            "department": "Electronics and Communications",
            "qualification": "M.Tech., Ph.D",
            "experience": "22 years",
            "email": "hod.ece@drttit.edu.in",
            "specialization": "Quantum Dots",
            "research": "Electrical Engineering"
        },
        "eee": {
            "name": "Dr. Lakshmipathy N",
            "department": "Electrical and Electronics",
            "qualification": "Ph.D",
            "experience": "23 years",
            "email": "hod.eee@drttit.edu.in",
            "specialization": "Illumination Design",
            "research": "Electrical Engineering"
        },
        "me": {
            "name": "Dr. Manas Mukhopadhyay",
            "department": "Mining",
            "qualification": "Ph.D",
            "experience": "28 years",
            "email": "dr.manas@drttit.edu.in",
            "specialization": "Slope Stability",
            "research": "Mining Engineering"
        },
        "meche": {
            "name": "Dr. Manjunatha Babu N S",
            "department": "Mechanical Engineering",
            "qualification": "M.Tech, Ph.D",
            "experience": "17 years",
            "email": "hod.mech@drttit.edu.in",
            "specialization": "Machining of Materials",
            "research": "Mechanical Engineering"
        },
        "aiml": {
            "name": "Dr. Geetha C. Megharaj",
            "department": "Computer Science",
            "qualification": "MS, M.TECH, PhD",
            "experience": "27 years",
            "email": "hodcse@drttit.edu.in",
            "specialization": "Computer Science Engineering",
            "research": "Artificial Intelligence"
        },
        "cive": {
            "name": "Dr. K. Ramesh",
            "department": "Civil Engineering",
            "qualification": "M.Sc, Ph.D",
            "experience": "18 years",
            "email": "hod.civ@drttit.edu.in",
            "specialization": "Remote sensing & GIS",
            "research": "Civil Engineering"
        },
        "maths": {
            "name": "Dr. Manjunath C",
            "department": "Mathematics",
            "qualification": "M.Sc., M.Phil., Ph.D",
            "experience": "20 years",
            "email": "hod.mat@drttit.edu.in",
            "specialization": "Number theory",
            "research": "Mathematics"
        },
        "physics": {
            "name": "Sarala Shanthi J",
            "department": "Physics",
            "qualification": "M.Sc., (Ph.D)",
            "experience": "27 years",
            "email": "hod.phy@drttit.edu.in",
            "specialization": "Solid State Physics",
            "research": "Physics"
        },
        "chemistry": {
            "name": "Mohana K R",
            "department": "Chemistry",
            "qualification": "M.Sc., B.Ed (Ph.D)",
            "experience": "29 years",
            "email": "hod.che@drttit.edu.in",
            "specialization": "Physical Chemistry",
            "research": "Chemistry"
        },
    }

    ADMINISTRATION = {
        "dean": {
            "name": "Prof. Ruckmani Divakaran",
            "position": "Dean of Academics",
            "email": "dean@drttit.edu.in",
            "responsibilities": "Academic planning and administration"
        },
        "vice principal": {
            "name": "Dr. H G Shenoy",
            "position": "Vice Principal",
            "email": "viceprincipal@drttit.edu.in",
            "responsibilities": "College administration and student affairs"
        }
    }

    JOKES = [
        "Why don't scientists trust atoms? They make up everything!",
        "What do you call fake spaghetti? An impasta!",
        "Why did the computer go to the doctor? It had a virus!",
        "Why was the math book sad? It had too many problems."
    ]

    def __init__(self):
        self.college_name = "Dr.TTIT College"
        self.principal_name = "Dr. Syed Ariff"
        self.principal_email = "principal@drttit.edu.in"
        self.vice_principal_name = self.ADMINISTRATION["vice principal"]["name"]
        self.vice_principal_email = self.ADMINISTRATION["vice principal"]["email"]
        self.dean_name = self.ADMINISTRATION["dean"]["name"]
        self.dean_email = self.ADMINISTRATION["dean"]["email"]
        self.contact_info = {
            'phone': '+91 081532 65413',
            'email': 'info@drttit.edu.in',
            'address': 'Dr. T. Thimmaiah Road, Band Line Colony, Oorgaumpet, Kolar Gold Fields, Robertsonpet, Karnataka 563120'
        }

    def format_response(self, user_input: str) -> Optional[str]:
        user_input = user_input.lower()
        for category, responses in self.RESPONSE_TEMPLATES.items():
            for keyword in sorted(responses.keys(), key=len, reverse=True):
                if keyword in user_input:
                    template = responses[keyword]
                    return template.format(
                        college_name=self.college_name,
                        principal_name=self.principal_name,
                        principal_email=self.principal_email,
                        vice_principal_name=self.vice_principal_name,
                        vice_principal_email=self.vice_principal_email,
                        dean_name=self.dean_name,
                        dean_email=self.dean_email,
                        **self.contact_info
                    )
        return None

    def get_professor_details(self, query: str) -> str:
        query = query.lower()

        for prof_id, prof in self.PROFESSORS.items():
            if prof_id in query:
                return self._format_professor_response(prof)

        for prof_id, prof in self.PROFESSORS.items():
            if any(word in query for word in prof_id.split()):
                return self._format_professor_response(prof)

        return self._list_all_professors()

    def _format_professor_response(self, prof: dict) -> str:
        response = (
            f"👨‍🏫 Professor Details:\n"
            f"Name: {prof['name']}\n"
            f"Department: {prof['department']}\n"
            f"Position: {prof.get('position', 'Professor')}\n"
            f"Qualification: {prof['qualification']}\n"
            f"Experience: {prof['experience']}\n"
        )

        if 'research' in prof:
            response += f"Research Areas: {prof['research']}\n"
        if 'specialization' in prof:
            response += f"Specialization: {prof['specialization']}\n"

        response += f"Email: {prof['email']}"
        return response

    def _list_all_professors(self) -> str:
        prof_list = "\n".join(
            f"- {prof['name']} ({prof['department']})"
            for prof in self.PROFESSORS.values()
        )
        return (
            f"📚 Professors at {self.college_name}:\n{prof_list}\n\n"
            "You can ask for details about a specific professor by name."
        )

    def get_hod_details(self, query: str) -> str:
        query = query.lower()

        for dept_code, hod in self.HODS.items():
            if dept_code in query:
                return self._format_hod_response(hod)

        for hod in self.HODS.values():
            if hod['department'].lower() in query:
                return self._format_hod_response(hod)

        return self._list_all_hods()

    def _format_hod_response(self, hod: dict) -> str:
        response = (
            f"👨‍💼 HOD Details:\n"
            f"Name: {hod['name']}\n"
            f"Department: {hod['department']}\n"
            f"Qualification: {hod['qualification']}\n"
            f"Experience: {hod['experience']}\n"
            f"Specialization: {hod['specialization']}\n"
            f"Research Areas: {hod['research']}\n"
            f"Email: {hod['email']}"
        )
        return response

    def _list_all_hods(self) -> str:
        hod_list = "\n".join(
            f"- {hod['name']} ({hod['department']})"
            for hod in self.HODS.values()
        )
        return (
            f"📌 Available HODs at {self.college_name}:\n{hod_list}\n\n"
            "You can ask about a specific department's HOD."
        )

    def get_administration_details(self, query: str) -> str:
        query = query.lower()
        for position, person in self.ADMINISTRATION.items():
            if position in query:
                return (
                    f"👨‍💼 {person['position']} Details:\n"
                    f"Name: {person['name']}\n"
                    f"Email: {person['email']}\n"
                    f"Responsibilities: {person.get('responsibilities', 'N/A')}"
                )
        return self._list_administration()

    def _list_administration(self) -> str:
        admin_list = "\n".join(
            f"- {person['name']} ({person['position']})"
            for person in self.ADMINISTRATION.values()
        )
        return (
            f"🏛️ College Administration:\n{admin_list}\n\n"
            "You can ask about specific positions like Principal, Vice Principal, or Dean."
        )

    def get_course_details(self, query: str) -> str:
        query = query.lower()

        for key, course in self.COURSE_DATA.items():
            if key in query:
                return self._format_course_response(course)

        for course in self.COURSE_DATA.values():
            if course['name'].lower() in query:
                return self._format_course_response(course)

        return self._list_all_courses()

    def _format_course_response(self, course: dict) -> str:
        return (
            f"📘 {course['name']}:\n"
            f"Duration: {course['duration']}\n"
            f"Fees: {course['fees']}\n"
            f"Specializations: {', '.join(course['specializations'])}\n"
            f"More Info: {self.college_name}{course['website']}"
        )

    def _list_all_courses(self) -> str:
        course_list = "\n".join(
            f"- {course['name']} ({code.upper()})"
            for code, course in self.COURSE_DATA.items()
        )
        return (
            f"📚 Available Courses at {self.college_name}:\n{course_list}\n\n"
            "You can ask for details about a specific course."
        )

    def get_current_time(self) -> str:
        now = datetime.datetime.now()
        return f"📅 Current Date & Time: {now.strftime('%A, %B %d, %Y %I:%M:%S %p')}"

    def tell_joke(self) -> str:
        return f"😂 {random.choice(self.JOKES)}"

    def search_web(self, query: str) -> str:
        if not query.strip():
            return "Please specify what you want me to search for."
        return f"🔍 Here's what I found: https://www.google.com/search?q={quote(query)}"

    def handle_transport_query(self, user_input: str) -> Optional[str]:
        user_input = user_input.lower()

    # Check for known locations
        for location, response in self.transport_locations.items():
            if location in user_input:
                return response

    # If no known location matches
        if "transport" in user_input:
            return "No! Our college provides transport facilities from various locations in Kolar district. Please specify your location for more details."

    def handle_course_offered_query(self, user_input: str) -> Optional[str]:
        user_input = user_input.lower()

    # Check for specific course codes or names
        for key, course in self.COURSE_DATA.items():
            if key in user_input or course['name'].lower() in user_input:
                return f"✅ Yes, we offer {course['name']} at our college. Would you like to know about its duration, fees, and specializations?"

    # Handle broader course-related keywords
        if "course" in user_input or "program" in user_input or "degree" in user_input:
            return self._list_all_courses()

        return "🚫 Sorry, i Don't understand what you said..."

    def handle_query(self, user_input: str) -> str:
        user_input = user_input.lower().strip()

        if not user_input:
            return "❗ Please type a question."

    # 1. Check for exact responses first
        exact_response = self.format_response(user_input)
        if exact_response:
            return exact_response

    # 2. Check transport queries
        transport_response = self.handle_transport_query(user_input)
        if transport_response:
            return transport_response

    # 3. Check for HOD queries BEFORE course offered queries
        patterns = {
            r'\b(?:hod|head of department)\b': self.get_hod_details,
            r'\b(?:principal|vice principal|dean|administration)\b': self.get_administration_details,
            r'\b(?:professor|faculty|lecturer|teacher)\b': self.get_professor_details,
            r'\b(?:course|program|degree)\b': self.get_course_details,
            r'\b(?:search|find|look up)\b': self.search_web,
            r'\b(?:time|date|current)\b': lambda _: self.get_current_time(),
            r'\b(?:joke|funny|humor)\b': lambda _: self.tell_joke(),
            r'\b(?:facilit(y|ies))\b': lambda _: self.RESPONSE_TEMPLATES["college_info"]["facilities"].format(college_name=self.college_name),
        }

        for pattern, handler in patterns.items():
            if re.search(pattern, user_input):
                query = re.sub(pattern, '', user_input).strip()
                return handler(query) if query else handler(user_input)

    # 4. Check course offered queries (moved down)
        course_offered_response = self.handle_course_offered_query(user_input)
        if course_offered_response:
            return course_offered_response

    # 5. Default response if no match is found
        return (
            "🤖 I can help you with:\n"
            "- 🎓 Course Information (CSE, ECE, EEE, etc.)\n"
            "- 🧑‍🏫 Professor Details\n"
            "- 👨‍💼 HOD Information\n"
            "- 🏛️ Administration Details\n"
            "- 📅 Date & Time\n"
            "- 📞 Contact Info\n"
            "- 😂 Jokes\n"
            "- 🔍 Web Searches\n"
            "- 🚌 Transport Information\n"
            "- 🏆 College Facilities\n\n"
            "Try asking about specific departments, courses, or faculty members.\n"
            "Example: 'Tell me about CSE course' or 'Who is the HOD of ECE?'"
        )



@require_GET
def get_response(request):
    user_input = request.GET.get('message', '').strip()

    if not user_input:
        return JsonResponse({'response': "❗ Please enter a message."})

    if len(user_input) > Chatbot.MAX_INPUT_LENGTH:
        return JsonResponse({'response': f"⚠️ Message exceeds {Chatbot.MAX_INPUT_LENGTH} characters."})

    try:
        bot = Chatbot()
        response = bot.handle_query(user_input)
        return JsonResponse({'response': response})
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return JsonResponse({'response': "⚠️ An error occurred. Please try again."})


def home(request):
    return render(request, 'index.html', {
        'current_year': datetime.datetime.now().year,
        'college_name': "Dr.TTIT College"
    })