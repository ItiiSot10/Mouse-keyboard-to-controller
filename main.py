from input_mapper import InputMapper

if __name__ == "__main__":
    try:
        mapper = InputMapper('config.yaml')
        mapper.run()
    except Exception as e:
        print(f"S'ha produït un error crític: {e}")
        print("Comprova que ViGEmBus estigui instal·lat i el config.yaml sigui correcte.")