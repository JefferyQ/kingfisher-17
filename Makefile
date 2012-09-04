# Helper for cleanup
.PHONY: clean

clean:
	$(RM) -rf MANIFEST dist/ build/ .coverage
	$(RM) -f kingfisher/*.pyc
