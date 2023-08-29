#!/usr/bin/env python3

import aws_cdk as cdk

from building_modern_apps_course.building_modern_apps_course_stack import (
    BuildingModernAppsCourseStack,
)


app = cdk.App()
BuildingModernAppsCourseStack(app, "building-modern-apps-course")

app.synth()
