import boto3

# Uses systems auth. Will fail if .aws isnt configed
CLIENT = boto3.client('ec2', region_name='us-east-1')


def main():
    enum_file = f'from enum import Enum{add_instance_enums()}{add_region_and_az_enums()}'

    # Create file
    with open("aws_enums/aws_enums.py", 'w') as output_file:
        output_file.write(enum_file)


def add_instance_enums() -> str:

    instance_blob = f"\n\nclass AWSInstanceTypes(Enum):"

    instances = CLIENT.describe_instance_types()
    next_token = True

    while next_token:

        for instance in instances['InstanceTypes']:
            instance_type = instance['InstanceType']

            instance_enum = instance_type.upper().replace('.', '_').replace('-', '_')
            instance_type = f"'{instance_type}'"

            instance_blob = f"{instance_blob}\n    {instance_enum} = {instance_type}"

        next_token = instances.get("NextToken")

        if next_token:
            instances = CLIENT.describe_instance_types(NextToken=next_token)

    return instance_blob


def add_region_and_az_enums() -> str:
    region_blob = f"\n\nclass AWSRegions(Enum):"
    zone_blob = f"\n\nclass AWSZones(Enum):"
    zone_id_blob = f"\n\nclass AWSZoneIDs(Enum):"
    regions = CLIENT.describe_regions()

    for region_info in regions['Regions']:
        region = region_info['RegionName']

        region_enum = region.upper().replace('-', '_')
        region_str = f"'{region}'"

        region_blob = f"{region_blob}\n    {region_enum} = {region_str}"

        zones = boto3.client('ec2', region).describe_availability_zones()

        for zone in zones['AvailabilityZones']:
            zone_name = zone['ZoneName']
            zone_enum = zone_name.upper().replace('-', '_')
            zone_str = f"'{zone_name}'"

            zone_blob = f"{zone_blob}\n    {zone_enum} = {zone_str}"

            zone_id = zone['ZoneId']
            zone_id_enum = zone_id.upper().replace('-', '_')
            zone_id_str = f"'{zone_id}'"

            zone_id_blob = f"{zone_id_blob}\n    {zone_id_enum} = {zone_id_str}"

    return f"{region_blob}\n{zone_blob}\n{zone_id_blob}"


if __name__ == '__main__':
    main()
