import type { MakerspaceLocation } from "./types";

export const api_endpoint =
  import.meta.env.VITE_API_ENDPOINT || "https://beta-api.cumaker.space";

// currently `YEAR-MONTH-DAY, YYYY-MM-DD`
export const format_date = (date: Date) => date.toISOString().split("T")[0];

export const locations = [
  {
    name: "Watt Family Innovation Center",
    tools: [
      "FDM 3D Printer (Plastic)",
      "SLA 3D Printer (Resin)",
      "3D Scanner",
      "CNC Mills",
      "Hand Tools",
      "Laser Cutter/Engraver",
      "Microelectronics & Soldering Supplies",
      "Part Pickup",
      "Visiting",
    ],
    fdm_printers: [
      "Mini 1",
      "Mini 2",
      "Mini 3",
      "Mini 4",
      "Mini 5",
      "Mini 6",
      "Mini 7",
      "Mini 8",
      "Mini 9",
      "Mini 10",
      "Mini 11",
      "Mini 12",
      "Taz 1",
      "Taz 2",
      "Taz 3",
      "Taz 4",
      "Taz 5",
      "Taz 6",
      "Taz 7",
      "Taz 8",
    ],
    sla_printers: ["Hopeful Terrier", "Inspiring Llama"],
  },
  {
    name: "Cooper Library",
    tools: [
      "FDM 3D Printer (Plastic)",
      "Button Maker",
      "Embroidery/Sewing Machine",
      "Fabric Printer",
      "Hand Tools",
      "Part Pickup",
      "Vinyl Cutter",
      "Visiting",
    ],
    fdm_printers: [
      "Adobe",
      "Adobe 1",
      "Adobe 2",
      "Adobe 3",
      "Adobe 4",
      "Adobe 5",
      "Adobe 6",
      "Adobe 7",
      "Adobe 8",
      "Adobe 9",
      "Adobe 10",
      "Adobe 11",
      "Adobe 12",
      "Adobe 13",
      "Adobe 14",
      "Adobe 15",
      "Adobe 16",
      "Taz A",
      "Taz B",
      "Taz C",
      "Taz D",
      "Taz E",
    ],
  },
  {
    name: "CU ICAR",
    tools: ["Waterjet", "Visiting"],
  },
];

export const genders = ["Male", "Female", "Other"];

export const userPosition = ["Undergraduate", "Graduate", "Faculty"];

export const gradsemesters = ["Fall", "Spring", "Summer"];

export const class_list = ["Freshman", "Sophomore", "Junior", "Senior"];

export const gradyears = Array.from({ length: 7 }, (v, i) =>
  String(i + new Date().getFullYear())
);

export const majors = [
  "Accounting",
  "Agribusiness",
  "Agricultural Education",
  "Agricultural Mechanization and Business",
  "Agriculture",
  "Animal and Veterinary Sciences",
  "Anthropology",
  "Applied Economics",
  "Applied Health Research and Evaluation",
  "Applied Psychology",
  "Architecture",
  "Art",
  "Athletic Leadership",
  "Automotive Engineering",
  "Biochemistry",
  "Biochemistry and Molecular Biology",
  "Bioengineering",
  "Biological Sciences",
  "Biomedical Engineering",
  "Biosystems Engineering",
  "Business Administration",
  "Chemical Engineering",
  "Chemistry",
  "City and Regional Planning",
  "Civil Engineering",
  "Communication",
  "Communication, Technology and Society",
  "Computer Engineering",
  "Computer Information Systems",
  "Computer Science",
  "Construction Science and Management",
  "Counselor Education",
  "Criminal Justice",
  "Curriculum and Instruction",
  "Data Science and Analytics",
  "Digital Production Arts",
  "Early Childhood Education",
  "Economics",
  "Educational Leadership",
  "Education Systems Improvement Science Ed.D.",
  "Electrical Engineering",
  "Elementary Education",
  "Engineering and Science Education",
  "English",
  "Entomology",
  "Environmental and Natural Resources",
  "Environmental Engineering",
  "Environmental Health Physics",
  "Environmental Toxicology",
  "Financial Management",
  "Food, Nutrition and Culinary Sciences",
  "Food, Nutrition and Packaging Sciences",
  "Food Science and Human Nutrition",
  "Food Technology",
  "Forest Resource Management",
  "Forest Resources",
  "Genetics",
  "Geology",
  "Graphic Communications",
  "Healthcare Genetics",
  "Health Science",
  "Historic Preservation",
  "History",
  "Horticulture",
  "Human-Centered Computing",
  "Human Capital Education and Development",
  "Human Factors Psychology",
  "Human Resource Development",
  "Hydrogeology",
  "Industrial Engineering",
  "Industrial/Organizational Psychology",
  "International Family and Community Studies",
  "Landscape Architecture",
  "Language and International Health",
  "Language and International Business",
  "Learning Sciences",
  "Literacy",
  "Literacy, Language and Culture",
  "Management",
  "Marketing",
  "Materials Science and Engineering",
  "Mathematical Sciences",
  "Mathematics Teaching",
  "Mechanical Engineering",
  "Microbiology",
  "Middle Level Education",
  "Modern Languages",
  "Nursing",
  "Packaging Science",
  "Pan African Studies",
  "Parks, Recreation and Tourism Management",
  "Philosophy",
  "Photonic Science and Technology",
  "Physics",
  "Planning, Design and Built Environment",
  "Plant and Environmental Sciences",
  "Policy Studies",
  "Political Science",
  "Prepharmacy",
  "Preprofessional Health Studies",
  "Preveterinary Medicine",
  "Performing Arts",
  "Professional Communication",
  "Psychology",
  "Public Administration",
  "Real Estate Development",
  "Religious Studies",
  "Resilient Urban Design",
  "Rhetorics, Communication and Information Design",
  "Science Teaching",
  "Secondary Education",
  "Sociology",
  "Social Science",
  "Special Education",
  "Sports Communication",
  "Student Affairs",
  "Teacher Residency",
  "Teaching and Learning",
  "Transportation Safety Administration",
  "Turfgrass",
  "Wildlife and Fisheries Biology",
  "Women's Leadership",
  "World Cinema",
  "Youth Development Leadership",
];

export const minors = [
  "Accounting",
  "Adult/Extension Education",
  "Aerospace Studies",
  "Agricultural Business Management",
  "Agricultural Mechanization and Business",
  "American Sign Language Studies",
  "Animal and Veterinary Sciences",
  "Anthropology",
  "Architecture",
  "Art",
  "Athletic Leadership",
  "Biochemistry",
  "Biological Sciences",
  "British and Irish Studies",
  "Brand Communications",
  "Business Administration",
  "Chemistry",
  "Chinese Studies",
  "Cluster",
  "Communication Studies",
  "Computer Science",
  "Creative Writing",
  "Crop and Soil Environmental Science",
  "Cybersecurity",
  "Digital Production Arts",
  "East Asian Studies",
  "Economics",
  "English",
  "Entomology",
  "Entrepreneurship",
  "Environmental Science and Policy",
  "Equine Industry",
  "Film Studies",
  "Financial Management",
  "Food Science",
  "Forest Products",
  "Forest Resource Management",
  "French Studies",
  "Gender, Sexuality and Women's Studies",
  "Genetics",
  "Geography",
  "Geology",
  "German Studies",
  "Global Politics",
  "Great Works",
  "History",
  "Horticulture",
  "Human Resource Management",
  "International Engineering and Science",
  "Italian Studies",
  "Japanese Studies",
  "Legal Studies",
  "Management",
  "Management Information Systems",
  "Mathematical Sciences",
  "Microbiology",
  "Middle Eastern Studies",
  "Military Leadership",
  "Music",
  "Natural Resource Economics",
  "Nonprofit Leadership",
  "Nuclear Engineering and Radiological Sciences",
  "Packaging Science",
  "Pan African Studies",
  "Park and Protected Area Management",
  "Philosophy",
  "Physics",
  "Plant Pathology",
  "Political and Legal Theory",
  "Political Science",
  "Precision Agriculture",
  "Psychology",
  "Public Policy",
  "Race, Ethnicity and Migration",
  "Religious Studies",
  "Russian Area Studies",
  "Science and Technology in Society",
  "Screenwriting",
  "Sociology",
  "Spanish Studies",
  "Spanish-American Area Studies",
  "Sustainability",
  "Theatre",
  "Travel and Tourism",
  "Turfgrass",
  "Urban Forestry",
  "Wildlife and Fisheries Biology",
  "Women's Leadership",
  "Writing",
  "Youth Development Studies",
];

export const equipmentTypes = [
  "FDM 3D Printer (Plastic)",
  "Laser Engraver",
  "Glowforge",
  "SLA 3D Printer (Resin)",
  "Fabric Printer",
  "Vinyl Cutter",
  "Button Maker",
  "3D Scanner",
  "Hand Tools",
  "Sticker Printer",
  "Embroidery Machine",
  "new thing",
];

export const projectTypes = ["Personal", "Class", "Club"];

export const surveryScores = [
  "10",
  "9",
  "8",
  "7",
  "6",
  "5",
  "4",
  "3",
  "2",
  "1",
];

export const surveyIssues = [
  "No issues",
  "Software issues",
  "Machine issues",
  "Intern issues",
];

export const interns = [
  "Drew",
  "Andrew",
  "Anna",
  "Braden",
  "Michael",
  "Taylor",
  "John",
  "Jack A",
  "Jack F",
  "Justin",
  "Katie",
  "Keller",
  "Kwasi",
  "Lucia",
  "Philip",
  "Lucy",
  "Nicolas",
  "Quinn",
  "Steven",
  "Thomas",
  "Zachary",
];
