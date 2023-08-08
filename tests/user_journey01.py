import json
import random
import argparse
from protosp03.recommendation import matchings


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    # Set seed for reproducibility
    random.seed(args.seed)

    # Define file paths
    inverted_index_job_path = "data/processed/synthetic/jobs_inverted_index.json"
    inverted_index_profile_path = (
        "data/processed/synthetic/profiles_inverted_index.json"
    )
    inverted_index_required_course_path = (
        "data/processed/synthetic/courses_required_inverted_index.json"
    )
    inverted_index_provided_course_path = (
        "data/processed/synthetic/courses_provided_inverted_index.json"
    )
    resume_path = "data/raw/synthetic/resumes.json"
    course_path = "data/raw/synthetic/courses.json"
    skill_path = "data/raw/synthetic/skills.json"
    job_path = "data/raw/synthetic/jobs.json"

    # Load data using context manager for handling file open/close
    with open(inverted_index_job_path, "r") as file:
        job_inverted_index = json.load(file)
    with open(inverted_index_profile_path, "r") as file:
        profile_inverted_index = json.load(file)
    with open(inverted_index_required_course_path, "r") as file:
        course_required_inverted_index = json.load(file)
    with open(inverted_index_provided_course_path, "r") as file:
        course_provided_inverted_index = json.load(file)

    with open(skill_path, "r") as file:
        skills = json.load(file)
    with open(resume_path, "r") as file:
        profiles = json.load(file)
    with open(job_path, "r") as file:
        jobs = json.load(file)
    with open(course_path, "r") as file:
        courses = json.load(file)

    # Choose a random profile and print its skills
    profile_id = random.choice(list(profiles.keys()))
    profile = profiles[profile_id]
    print(f"Considering Profile {profile_id} with the skills: {profile}")

    # Assume the profile is interested in a random job and print its skills
    interest_job = random.choice(list(jobs.keys()))
    print(
        f"\tWe are assuming that the Profile is interested in Job {interest_job} that requires the skills: {jobs[interest_job]}"
    )

    # Compute and print the matching between the profile and the desired job
    profile_job_matching = matchings.profile_job_match(profile, jobs[interest_job])
    print(
        f"\tThe matching between the profile and the desired job is: {int(profile_job_matching)}%"
    )

    print(
        f"\tPrinting the attractiveness of each skill of the profile and comparing to other learners:"
    )
    for skill in profile:
        if skill not in job_inverted_index:
            print(f"\t\tSkill {skill} is not required for any job on the market")
            continue
        skill_attractiveness = 100 * len(job_inverted_index[skill]) / len(jobs)
        skill_uniqueness = 100 * len(profile_inverted_index[skill]) / len(profiles)
        print(
            f"\t\tSkill {skill} is required for {int(skill_attractiveness)}% of the jobs on the market and {int(skill_uniqueness)}% of the learners have it"
        )

    # Compute matchings of the profile with respect to each job
    ranked_jobs = matchings.profile_alljobs_match(profile, jobs, job_inverted_index)
    overall_job_attractiveness = ranked_jobs.total() / len(jobs)

    print(
        f"\tThe overall attractiveness of the profile is: {int(overall_job_attractiveness)}%"
    )
    print(
        f"\tPrinting the matching of the profile with respect to each job (from most compatible to least compatible):"
    )
    for job, matching in ranked_jobs.most_common():
        print(f"\t\tJob {job} has a matching of {int(matching)}%")

    print(
        f"\tPrinting the matching of the profile with respect to each course (from most compatible to least compatible):"
    )
    ranked_courses = matchings.profile_allcourse_requirements(
        profile, courses, course_required_inverted_index
    )
    for course, profile_course_requirement_matching in ranked_courses.most_common():
        print(
            f"\t\tCourse {course} has a matching of {int(profile_course_requirement_matching)}%"
        )

        # Compute and print the effect of taking a course on the matching with the job and the overall attractiveness
        tmp_profile = profile.copy()
        tmp_profile.update(courses[course]["provided"])

        # learned_skills = tmp_profile.keys().difference(profile.keys())
        learned_skills = {
            skill for skill in courses[course]["provided"] if skill not in profile
        }
        upgraded_skills = {
            skill
            for skill in profile
            if skill in tmp_profile and tmp_profile[skill] > profile[skill]
        }

        new_profile_job_matching = matchings.profile_job_match(
            tmp_profile, jobs[interest_job]
        )
        new_ranked_jobs = matchings.profile_alljobs_match(
            tmp_profile, jobs, job_inverted_index
        )
        new_overall_job_attractiveness = new_ranked_jobs.total() / len(jobs)
        print(
            f"\t\t\tIf the profile takes the course {course}, it will learn the new skills: {learned_skills}"
        )
        print(
            f"\t\t\tIf the profile takes the course {course}, it will upgrade the skills: {upgraded_skills}"
        )
        print(
            f"\t\t\tThe matching with the job {interest_job} will increase from {int(profile_job_matching)}% to: {int(new_profile_job_matching)}%"
        )
        print(
            f"\t\t\tThe overall attractiveness of the profile will increase from {int(overall_job_attractiveness)} to: {int(new_overall_job_attractiveness)}"
        )

    print()


if __name__ == "__main__":
    main()
