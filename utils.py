def match_symptoms_to_specialist(symptoms, symptom_mapping):
    """
    Match patient symptoms to the appropriate medical specialist
    
    Args:
        symptoms (str): Patient's described symptoms
        symptom_mapping (dict): Mapping of symptoms to specialists
    
    Returns:
        str: The recommended specialist type
    """
    symptoms_lower = symptoms.lower()
    
    # Count matches for each specialty
    specialty_matches = {}
    
    for symptom_key, specialist in symptom_mapping.items():
        if symptom_key in symptoms_lower:
            specialty_matches[specialist] = specialty_matches.get(specialist, 0) + 1
    
    # If no matches found, default to General Physician
    if not specialty_matches:
        return "Cardiologist"  # Default to a common specialist if no match
    
    # Return the specialist with the most symptom matches
    return max(specialty_matches.items(), key=lambda x: x[1])[0]
