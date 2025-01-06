from faker.proxy import Faker

faker = Faker()

popular_names = [ faker.name() for i in range(10)]

print(popular_names)